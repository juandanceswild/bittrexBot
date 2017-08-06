__author__ = 'chase.ufkes'

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