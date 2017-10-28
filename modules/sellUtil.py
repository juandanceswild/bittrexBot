__author__ = 'zaphodbeeblebrox'

import bittrex

def cancelOrder(orderInventory, orders, apiKey, apiSecret):
    api = bittrex.bittrex(apiKey, apiSecret)
    ordersToKill = orders - 1
    for sellOrder in orderInventory:
        while (ordersToKill >  0):
            api.cancel(sellOrder['OrderUuid'])
            ordersToKill = ordersToKill - 1

def sellNumber(orderInventory):
    orderCount = 0
    for order in orderInventory:
        if (order['OrderType'] == 'LIMIT_SELL'):
            orderCount = orderCount + 1
    return orderCount

def defSellValue(orderValueHistory, sellValuePercent):
    newSellValue = round((orderValueHistory * (sellValuePercent * .01)) + orderValueHistory, 8)
    return newSellValue

def defSellVolume(orderVolume, sellVolumePercent):
    newSellVolume = round(orderVolume * (sellVolumePercent * .01), 8)
    return newSellVolume