__author__ = 'chase.ufkes'

import bittrex

def lastOrderValue(market, apiKey, apiSecret):
    api = bittrex.bittrex(apiKey, apiSecret)
    lastOrder = api.getorderhistory(market, 0)
    if lastOrder:
        return lastOrder[0]['PricePerUnit']
    else:
        currentValue = api.getmarketsummary(market)
        currentValue = currentValue[0]['Last']
        return currentValue