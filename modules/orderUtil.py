__author__ = 'chase.ufkes'

# get the number of current sell orders
def sellNumber(orderInventory):
    orderCount = 0
    for order in orderInventory:
        if (order['OrderType'] == 'LIMIT_SELL'):
            orderCount = orderCount + 1
    return orderCount

# get the number of current buy orders
def buyNumber(orderInventory):
    orderCount = 0
    for order in orderInventory:
        if (order['OrderType'] == 'LIMIT_BUY'):
            orderCount = orderCount + 1
    return orderCount

# determine the number of coins to buy
def defBuyValue(orderValueHistory, buyValuePercent):
    newBuyValue = round(orderValueHistory - (orderValueHistory * (buyValuePercent * .01)), 8)
    return newBuyValue

# determine the price to pay
def defBuyVolume(orderVolume, buyVolumePercent):
    newBuyVolume = round((orderVolume * (buyVolumePercent * .01)), 8)
    return newBuyVolume

# determine the number of coins to buy
def defSellValue(orderHistory, sellValuePercent):
    newSellValue = round((orderHistory * (sellValuePercent * .01)) + orderHistory, 8)
    return newSellValue

# determine the price to buy the coins at
def defSellVolume(orderVolume, sellVolumePercent):
    newSellVolume = round(orderVolume * (sellVolumePercent * .01), 8)
    return newSellVolume