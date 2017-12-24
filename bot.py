#!/usr/bin/env python
__author__ = 'chase.ufkes'

import time
import json
import gc
from modules import bittrex
from modules import orderUtil
from modules import buyUtil
from modules import sellUtil

with open("config/botConfig.json", "r") as fin:
    config = json.load(fin)

apiKey = str(config['apiKey'])
apiSecret = str(config['apiSecret'])
trade = config['trade']
currency = config['currency']
sellValuePercent = config.get('sellValuePercent', 4)
sellVolumePercent = config.get('sellVolumePercent', 0)
buyValuePercent = config.get('buyValuePercent', 4)
buyVolumePercent = config.get('buyVolumePercent', 0)
extCoinBalance = config.get('extCoinBalance', 0)
checkInterval = config.get('checkInterval', 30)
initialSellPrice = config.get('initialSellPrice', 0)
tradeAmount = config.get('tradeAmount', 0)
#new method -- stop loss/limit
# stopLossLimit = config.get('stopLossLimit', 'false')
# stopLossPercent = config.get('stopLossPercent', 4)

#new method -- enter/exit
enterExit = config.get('enterExit', 'false')
enterPrice = config.get('enterPrice', 0)
exitPrice = config.get('exitPrice', 0)

if (initialSellPrice != 0):
    initialSellPrice = config['initialSellPrice']
    float(initialSellPrice)
    print initialSellPrice

if (sellValuePercent == 0 or enterExit == 'true'):
    blockSell = 'true'
else:
    blockSell = 'false'

if (buyValuePercent == 0  or enterExit == 'true'):
    blockBuy = 'true'
else:
    blockBuy = 'false'

api = bittrex.bittrex(apiKey, apiSecret)
market = '{0}-{1}'.format(trade, currency)

# Get the number of sell orders and if there's more than 1 open, close. 
# Returns 1 or 0 (or cancels all the orders)
def control_sell_orders(orderInventory):
    orders = sellUtil.sellNumber(orderInventory) # count open sell orders
    if (orders == 1): # 
        return 1
    elif (orders > 1):
        sellUtil.cancelOrder(orderInventory, orders, apiKey, apiSecret)
    else:
        return 0

def control_buy_orders(orderInventory):
    orders = buyUtil.buyNumber(orderInventory)
    if (orders == 1):
        return 1
    elif (orders > 1):
        buyUtil.cancelOrder(orderInventory, orders, apiKey, apiSecret)
    else:
        return 0

def set_initial_buy(buyVolumePercent, orderVolume, market, buyValuePercent, currentValue):
    newBuyValue = buyUtil.defBuyValue(currentValue, buyValuePercent)
    if (buyVolumePercent == 0):
        newBuyVolume = tradeAmount
    else:
        newBuyVolume = buyUtil.defBuyVolume(orderVolume, buyVolumePercent)
    result = api.buylimit(market, newBuyVolume, newBuyValue)
    print result

def set_initial_sell(sellVolumePercent, orderVolume, market, sellValuePercent, currentValue):
    if (initialSellPrice > currentValue):
        print "Setting user defined sell value"
        newSellValue = initialSellPrice
    else:
        print "Setting sellValue to market conditions"
        newSellValue = sellUtil.defSellValue(currentValue, sellValuePercent)
    if (sellVolumePercent == 0):
        newSellVolume = tradeAmount
    else:
        newSellVolume = sellUtil.defSellVolume(orderVolume, sellVolumePercent)
    result = api.selllimit(market, newSellVolume, newSellValue)
    print result

print "checking value"
currentValue = orderUtil.initialMarketValue(market, apiKey, apiSecret)
orderInventory = orderUtil.orders(market, apiKey, apiSecret) #prepare to reset orders
orderUtil.resetOrders(orderInventory, apiKey, apiSecret)
if api.getbalance(currency)['Balance'] is None:
    balance = 0
else:
    balance = api.getbalance(currency)['Balance']

print "balance is " + str(balance)
orderVolume = balance + extCoinBalance

if blockBuy == 'false':
    print tradeAmount
    set_initial_buy(buyVolumePercent, orderVolume, market, buyValuePercent, currentValue)
if blockSell == 'false':
    print tradeAmount
    set_initial_sell(sellVolumePercent, orderVolume, market, sellValuePercent, currentValue)


looping = True
cycle = 0


#new Method Enter/Exit
# 1. Open Buy order at enter price
# 1.5 Set buy mode
# 2. on each cycle, check buy order
# 3. If there are no open buy orders and in buy mode - means the order filled, open sell order
# 4. Set sell mode
# 5. If there are no open orders and sell mode, trade finished.
if enterExit == 'true':
    enterExitCycle = 'buy'
    buyVolume = tradeAmount
    buyValue = enterPrice
    print "Currency: " + currency
    print "Buy Value: " + str(buyValue)
    print "Buy Volume: " + str(buyVolume)
    print "Setting buy entry order..."
    result = api.buylimit(market, buyVolume, buyValue)
    print result

time.sleep(checkInterval)

while looping:
    cycle = cycle + 1
    try:
        orderInventory = orderUtil.orders(market, apiKey, apiSecret) # gets all currently open orders
        orderUtil.recentTransaction(market, orderInventory, apiKey, apiSecret, checkInterval) # check the last closed order and resets all orders if an order has closed recently (before the following check).
        orderValueHistory = orderUtil.lastOrderValue(market, apiKey, apiSecret) # Last order value (sell or buy price per unit)
        orderVolume = api.getbalance(currency)['Balance'] + extCoinBalance # get the total volume of the coin in the account

        if enterExit == 'true':
            if enterExitCycle == 'buy':
                buyControl = control_buy_orders(orderInventory)
                print "Orders open: " + str(buyControl)
                print "Buying " + str(buyVolume) + " " + currency + " at " + str(buyValue)
                if (buyControl == 0): # buy order was filled.
                    enterExitCycle = 'sell'
                    sellVolume = tradeAmount
                    sellValue = exitPrice
                    print "Currency: " + currency
                    print "Sell Value: " + str(sellValue)
                    print "Sell Volume: " + str(sellVolume)
                    print "Setting sell entry order..."
                    result = api.selllimit(market, sellVolume, sellValue) # Set sell order.
                    print result

            if enterExitCycle == 'sell':
                sellControl = control_sell_orders(orderInventory)
                if (sellControl == 0):
                    print "Completed exit order at" + str(orderValueHistory)
                    looping = False



        if blockSell == 'false':
            sellControl = control_sell_orders(orderInventory) # get the number of sell orders open (should be 1 or 0)
            if (sellControl == 0): # if no open sell orders -- my previous order filled
                newSellValue = sellUtil.defSellValue(orderValueHistory, sellValuePercent)  #calculate new sell value based on the last successful trade
                if (sellVolumePercent == 0): # if new sell volume is set by quantity,
                    print "Setting user defined trade amount"
                    print tradeAmount
                    newSellVolume = tradeAmount # set new sell volume from config
                else: # if new sell volume is set by %
                    newSellVolume = sellUtil.defSellVolume(orderVolume, sellVolumePercent) # calculate new sell volume by percentage
                print "Currency: " + currency
                print "Sell Value: " + str(newSellValue)
                print "Sell volume: " + str(newSellVolume)
                print "Setting sell order..."
                result = api.selllimit(market, newSellVolume, newSellValue) # open a limit sell order
                print result
            # if stopLossLimit = 'true':
                # check open sell orders and if the current price of the coin is the percentage below stopLossPercent, cancel all sell orders and open a sell order at market price.
                # stopLossValue = price of the last sell order - percent of sell - percent of stopLoss
                # stopLossValue = orderInventory[0]['PricePerUnit'] * (1 - sellVolumePercent - stopLossPercent) 
                # if (orderValueHistory <= stopLossValue)
                    # orderUtil.

        if blockBuy == 'false': # and stopLossLimit = 'false':
            buyControl = control_buy_orders(orderInventory)
            if (buyControl == 0): # Creates new buy order.
                newBuyValue = buyUtil.defBuyValue(orderValueHistory, buyValuePercent)
                if (buyVolumePercent == 0):
                    print "Setting user defined trade amount "
                    print tradeAmount
                    newBuyVolume = tradeAmount
                else:
                    newBuyVolume = buyUtil.defBuyVolume(orderVolume, buyVolumePercent)
                print "Currency: " + currency
                print "Buy Value: " + str(newBuyValue)
                print "Buy Volume: " + str(newBuyVolume)
                print "Setting buy order..."
                result = api.buylimit(market, newBuyVolume, newBuyValue)
                print result

    except:
        print "Bittrex probably threw a 503...trying again on the next cycle"

    if cycle == 100:
        print "Garbage collection"
        gc.collect()
        count = 0
    time.sleep(checkInterval)