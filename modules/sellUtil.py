__author__ = 'zaphodbeeblebrox'

import bittrex

# cancel sell order
def cancelOrder(orderInventory, orders, apiKey, apiSecret):
    api = bittrex.bittrex(apiKey, apiSecret)
    ordersToKill = orders - 1
    for sellOrder in orderInventory:
        while (ordersToKill >  0):
            api.cancel(sellOrder['OrderUuid'])
            ordersToKill = ordersToKill - 1

# get the number of current sell orders
def sellNumber(orderInventory):
    orderCount = 0
    for order in orderInventory:
        if (order['OrderType'] == 'LIMIT_SELL'):
            orderCount = orderCount + 1
    return orderCount

# determine the number of coins to buy
def defSellValue(orderValueHistory, sellValuePercent):
    newSellValue = round((orderValueHistory * (sellValuePercent * .01)) + orderValueHistory, 8)
    return newSellValue

# determine the price to buy the coins at
def defSellVolume(orderVolume, sellVolumePercent):
    newSellVolume = round(orderVolume * (sellVolumePercent * .01), 8)
    return newSellVolume