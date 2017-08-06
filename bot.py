#!/usr/bin/env python
__author__ = 'chase.ufkes'

import time
import datetime
import re
import json
from modules import bittrex
from modules import orderUtil
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

def get_orders(market):
    orderInventory = api.getopenorders(market)
    return orderInventory

def get_number_of_sell_orders(orderInventory):
    orderCount = sellUtil.sellNumber(orderInventory)
    return orderCount

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

def set_initial_buy(buyVolumePercent, orderVolume, market, buyValuePercent, orderValueHistory):
    newBuyValue = orderUtil.defBuyValue(orderValueHistory, buyValuePercent)
    newBuyVolume = orderUtil.defBuyVolume(orderVolume, buyVolumePercent)
    result = api.buylimit(market, newBuyVolume, newBuyValue)
    print result

def set_initial_sell(sellVolumePercent, orderVolume, market, sellValuePercent, orderValueHistory):
    newSellValue = sellUtil.defSellValue(orderValueHistory, sellValuePercent)
    newSellVolume = sellUtil.defSellVolume(orderVolume, sellVolumePercent)
    result = api.selllimit(market, newSellVolume, newSellValue)
    print result


#setting buy / sells during startup to avoid crap selling
currentValue = orderUtil.lastOrderValue(market, apiKey, apiSecret)
orderInventory = get_orders(market) #prepare to reset orders
reset_orders(orderInventory)
time.sleep(2)
orderValueHistory = orderUtil.lastOrderValue(market, apiKey, apiSecret)
orderVolume = api.getbalance(currency)['Available'] + extCoinBalance
set_initial_buy(buyVolumePercent, orderVolume, market, buyValuePercent, orderValueHistory)
set_initial_sell(sellVolumePercent, orderVolume, market, sellValuePercent, orderValueHistory)
time.sleep(2)
while True:
    orderInventory = get_orders(market)
    check_for_recent_transaction(market, orderInventory)
    sellControl = control_sell_orders(orderInventory)
    buyControl = control_buy_orders(orderInventory)
    orderValueHistory = orderUtil.lastOrderValue(market, apiKey, apiSecret)
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