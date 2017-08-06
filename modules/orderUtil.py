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

def lastOrderValue(market, apiKey, apiSecret):
    api = bittrex.bittrex(apiKey, apiSecret)
    lastOrder = api.getorderhistory(market, 0)
    if lastOrder:
        return lastOrder[0]['PricePerUnit']
    else:
        currentValue = api.getmarketsummary(market)
        currentValue = currentValue[0]['Last']
        return currentValue