#!/usr/bin/env python
__author__ = 'chase.ufkes'

import time
import json
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
sellValuePercent = config['sellValuePercent']
buyValuePercent = config['buyValuePercent']
buyVolumePercent = config['buyVolumePercent']
sellVolumePercent = config['sellVolumePercent']
extCoinBalance = config['extCoinBalance']
checkInterval = config['checkInterval']

api = bittrex.bittrex(apiKey, apiSecret)
market = '{0}-{1}'.format(trade, currency)

def kill_sell_order(orderInventory, orders):
    sellUtil.cancelOrder(orderInventory, orders, apiKey, apiSecret)

def control_sell_orders(orderInventory):
    orders = sellUtil.sellNumber(orderInventory)
    if (orders == 1):
        return 1
    elif (orders > 1):
        (orderInventory, orders)
    else:
        return 0

def kill_buy_order(orderInventory, orders):
    ordersToKill = orders - 1
    for buyOrder in orderInventory:
        while (ordersToKill >  0):
            api.cancel(buyOrder['OrderUuid'])
            ordersToKill = ordersToKill - 1

def control_buy_orders(orderInventory):
    orders = buyUtil.buyNumber(orderInventory)
    if (orders == 1):
        return 1
    elif (orders > 1):
        kill_buy_order(orderInventory, orders)
    else:
        return 0

def set_initial_buy(buyVolumePercent, orderVolume, market, buyValuePercent, orderValueHistory):
    newBuyValue = buyUtil.defBuyValue(orderValueHistory, buyValuePercent)
    newBuyVolume = buyUtil.defBuyVolume(orderVolume, buyVolumePercent)
    result = api.buylimit(market, newBuyVolume, newBuyValue)
    print result

def set_initial_sell(sellVolumePercent, orderVolume, market, sellValuePercent, orderValueHistory):
    newSellValue = sellUtil.defSellValue(orderValueHistory, sellValuePercent)
    newSellVolume = sellUtil.defSellVolume(orderVolume, sellVolumePercent)
    result = api.selllimit(market, newSellVolume, newSellValue)
    print result


#setting buy / sells during startup to avoid crap selling
currentValue = orderUtil.lastOrderValue(market, apiKey, apiSecret)
orderInventory = orderUtil.orders(market, apiKey, apiSecret) #prepare to reset orders
orderUtil.resetOrders(orderInventory, apiKey, apiSecret)
orderValueHistory = orderUtil.lastOrderValue(market, apiKey, apiSecret)
orderVolume = api.getbalance(currency)['Available'] + extCoinBalance
set_initial_buy(buyVolumePercent, orderVolume, market, buyValuePercent, orderValueHistory)
set_initial_sell(sellVolumePercent, orderVolume, market, sellValuePercent, orderValueHistory)
time.sleep(2)

while True:
    orderInventory = orderUtil.orders(market, apiKey, apiSecret)
    orderUtil.recentTransaction(market, orderInventory, apiKey, apiSecret, checkInterval)
    sellControl = control_sell_orders(orderInventory)
    buyControl = control_buy_orders(orderInventory)
    orderValueHistory = orderUtil.lastOrderValue(market, apiKey, apiSecret)
    orderVolume = api.getbalance(currency)['Available'] + extCoinBalance

    if (sellControl == 0):
        newSellValue = sellUtil.defSellValue(orderValueHistory, sellValuePercent)
        newSellVolume = sellUtil.defSellVolume(orderVolume, sellVolumePercent)
        print "Currency: " + currency
        print "Sell Value: " + str(newSellValue)
        print "Sell volume: " + str(newSellVolume)
        result = api.selllimit(market, newSellVolume, newSellValue)
        print result

    if (buyControl == 0):
        newBuyValue = buyUtil.defBuyValue(orderValueHistory, buyValuePercent)
        newBuyVolume = buyUtil.defBuyVolume(orderVolume, buyVolumePercent)
        print "Currency: " + currency
        print "Buy Value: " + str(newBuyValue)
        print "Buy Volume: " + str(newBuyVolume)
        result = api.buylimit(market, newBuyVolume, newBuyValue)
        print result
    time.sleep(checkInterval)