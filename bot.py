#!/usr/bin/env python
__author__ = 'chase.ufkes'

# TODO
# note the code
# make it more readable

import time
import datetime
import re
import json
from modules import bittrex
from modules import orderUtil

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


def get_orders(market):
    orderInventory = api.getopenorders(market)
    return orderInventory

def get_number_of_sell_orders(orderInventory):
    orderCount = orderUtil.sellNumber(orderInventory)
    return orderCount

def kill_sell_order(orderInventory, orders):
    ordersToKill = orders - 1
    for sellOrder in orderInventory:
        while (ordersToKill >  0):
            api.cancel(sellOrder['OrderUuid'])
            ordersToKill = ordersToKill - 1

def control_sell_orders(orderInventory):
    orders = get_number_of_sell_orders(orderInventory)
    if (orders == 1):
        return 1
    elif (orders > 1):
        kill_sell_order(orderInventory, orders)
    else:
        return 0

def get_number_of_buy_orders(orderInventory):
    orderCount = orderUtil.buyNumber(orderInventory)
    return orderCount

def kill_buy_order(orderInventory, orders):
    ordersToKill = orders - 1
    for buyOrder in orderInventory:
        while (ordersToKill >  0):
            api.cancel(buyOrder['OrderUuid'])
            ordersToKill = ordersToKill - 1

def control_buy_orders(orderInventory):
    orders = get_number_of_buy_orders(orderInventory)
    if (orders == 1):
        return 1
    elif (orders > 1):
        kill_buy_order(orderInventory, orders)
    else:
        return 0

def get_last_order_value(market):
    lastOrder = api.getorderhistory(market, 0)
    if lastOrder:
        return lastOrder[0]['PricePerUnit']
    else:
        return get_initial_market_value(market)

def check_for_recent_transaction(market, orderInventory):
    lastOrder = api.getorderhistory(market, 0)
    if lastOrder:
        lastOrder = lastOrder[0]['Closed']
        orderTime = re.sub('T', ' ', lastOrder)
        orderTime = datetime.datetime.strptime(orderTime,  "%Y-%m-%d %H:%M:%S.%f").replace(microsecond=0)
        print orderTime
        currentTime = datetime.datetime.utcnow()
        difference = currentTime - orderTime

        if difference.total_seconds() < checkInterval:
            reset_orders(orderInventory)
            time.sleep(2)

def reset_orders(orderInventory):
    for order in orderInventory:
        print "Removing order: " + order['OrderUuid']
        api.cancel(order['OrderUuid'])

def get_initial_market_value(market):
    currentValue = api.getmarketsummary(market)
    currentValue = currentValue[0]['Last']
    return currentValue

def set_initial_buy(currentValue, buyVolumePercent, orderVolume, market, buyValuePercent):
    newBuyValue = orderUtil.defBuyValue(orderValueHistory, buyValuePercent)
    newBuyVolume = orderUtil.defBuyVolume(orderVolume, buyVolumePercent)
    result = api.buylimit(market, newBuyVolume, newBuyValue)
    print result

def set_initial_sell(currentValue, sellVolumePercent, orderVolume, market, sellValuePercent):
    newSellValue = orderUtil.defSellValue(orderHistory, sellValuePercent)
    newSellVolume = orderUtil.defSellVolume(orderVolume, sellVolumePercent)
    result = api.selllimit(market, newSellVolume, newSellValue)
    print result


#setting buy / sells during startup to avoid crap selling
currentValue = get_initial_market_value(market)
orderInventory = get_orders(market) #prepare to reset orders
reset_orders(orderInventory)
time.sleep(2)
orderVolume = api.getbalance(currency)['Available'] + extCoinBalance
set_initial_buy(currentValue, buyVolumePercent, orderVolume, market, buyValuePercent)
set_initial_sell(currentValue, sellVolumePercent, orderVolume, market, sellValuePercent)
time.sleep(2)
while True:
    orderInventory = get_orders(market)
    check_for_recent_transaction(market, orderInventory)
    sellControl = control_sell_orders(orderInventory)
    buyControl = control_buy_orders(orderInventory)
    orderValueHistory = get_last_order_value(market)
    orderVolume = api.getbalance(currency)['Available'] + extCoinBalance

    if (sellControl == 0):
        newSellValue = orderUtil.defSellValue(orderHistory, sellValuePercent)
        newSellVolume = orderUtil.defSellVolume(orderVolume, sellVolumePercent)
        print "Currency: " + currency
        print "Sell Value: " + str(newSellValue)
        print "Sell volume: " + str(newSellVolume)
        result = api.selllimit(market, newSellVolume, newSellValue)
        print result

    if (buyControl == 0):
        newBuyValue = orderUtil.defBuyValue(orderValueHistory, buyValuePercent)
        newBuyVolume = orderUtil.defBuyVolume(orderVolume, buyVolumePercent)
        print "Currency: " + currency
        print "Buy Value: " + str(newBuyValue)
        print "Buy Volume: " + str(newBuyVolume)
        result = api.buylimit(market, newBuyVolume, newBuyValue)
        print result
    time.sleep(checkInterval)