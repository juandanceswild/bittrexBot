__author__ = 'chase.ufkes'

import time
import bittrex
import datetime
import re

# retrieve the value of the last order
def lastOrderValue(market, apiKey, apiSecret):
    api = bittrex.bittrex(apiKey, apiSecret)
    lastOrder = api.getorderhistory(market, 0)
    if lastOrder:
        return lastOrder[0]['PricePerUnit']
    else:
        currentValue = api.getmarketsummary(market)
        currentValue = currentValue[0]['Last']
        return currentValue

# checks for a closed transaction within the checkInterval limit,
# if a transaction has occured within the check, remove orders for the token
def recentTransaction(market, orderInventory, apiKey, apiSecret, checkInterval):
    api = bittrex.bittrex(apiKey, apiSecret)
    lastOrder = api.getorderhistory(market, 0)
    if lastOrder:
        lastOrder = lastOrder[0]['Closed']
        orderTime = re.sub('T', ' ', lastOrder)
        orderTime = datetime.datetime.strptime(orderTime,  "%Y-%m-%d %H:%M:%S.%f").replace(microsecond=0)
        print orderTime
        currentTime = datetime.datetime.utcnow()
        difference = currentTime - orderTime
        if difference.total_seconds() < checkInterval:
            resetOrders(orderInventory, apiKey, apiSecret)

# retrieve a list of all open orders
def orders(market, apiKey, apiSecret):
    api = bittrex.bittrex(apiKey, apiSecret)
    orderInventory = api.getopenorders(market)
    return orderInventory

# resets open orders for the token
def resetOrders(orderInventory, apiKey, apiSecret):
    api = bittrex.bittrex(apiKey, apiSecret)
    for order in orderInventory:
        print "Removing order: " + order['OrderUuid']
        api.cancel(order['OrderUuid'])
        time.sleep(2)