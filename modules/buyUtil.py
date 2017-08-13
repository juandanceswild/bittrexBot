__author__ = 'chase.ufkes'

import bittrex

# get the number of current buy orders
def buyNumber(orderInventory):
    orderCount = 0
    for order in orderInventory:
        if (order['OrderType'] == 'LIMIT_BUY'):
            orderCount = orderCount + 1
    return orderCount

# determine the number of coins to buy
def defBuyValue(orderHistory, buyValuePercent):
    newBuyValue = round(orderHistory - (orderHistory * (buyValuePercent * .01)), 8)
    return newBuyValue

# determine the price to pay
def defBuyVolume(orderVolume, buyVolumePercent):
    newBuyVolume = round((orderVolume * (buyVolumePercent * .01)), 8)
    return newBuyVolume

def cancelOrder(orderInventory, orders, apiKey, apiSecret):
    api = bittrex.bittrex(apiKey, apiSecret)
    ordersToKill = orders - 1
    for buyOrder in orderInventory:
        while (ordersToKill >  0):
            api.cancel(buyOrder['OrderUuid'])
            ordersToKill = ordersToKill - 1