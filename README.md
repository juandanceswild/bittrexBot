Questions feel free to ask

# bittrexBot
This is an experimental bot for swing trading against the bittrex exchange. Set an upper and lower percentage that will place buy / sell orders. When an order triggers, the bracket will shift basing off the last order.

**This bot is designed to trade coins you currently have! At current, it does not support trying to trade on a currency of which you have a 0 balance.**

**Example: if you try to execute it on ZEC but have no ZEC coins, it will not work**

# DISCLAIMER

### I am not responsible for anything done with this bot. You use it at your own risk. There are no warranties or guarantees expressed or implied. You assume all responsibility and liability.

## Configuration

#### Note: An api key will need to be created with "Trade Limit" permissions

* apiKey - api key
* apiSecret - api key secret
* trade - the base token used for exchange
* currency - the token ticker to be traded
* sellValuePercent - the difference in the sell price of the previous order completed
* buyValuePercent - the difference in the buy price of the previous order completed
* sellVolumePercent - how many tokens are traded during a transaction
* buyVolumePercent - how many tokens to purchase. Set this number higher than the sellVolumePercent to accumulate more tokens...set it lower to purge tokens
* extCoinBalance - off exchange token count
* checkInterval - how often the bot will check for orders
* initialSellPrice - **OPTIONAL** price the bot sets on first startup (example: 0.00095). Leave at 0 to set to current market conditions

*Specal Options*

* Adding a sat value to the initialSellVolume configuration sets the first sell price at startup
* Leaving sell value and / or percent out of the config will disable placement of sell orders. Buys will still place and when they trigger, the bracket will still shift.
* Leaving buy value and / or percent out of the config will disable placement of buy orders. Sells will still place and when they trigger, the bracket will still shift.

The percentage values are actual percentages...not decimals. So if you want to trade 3.25% you would input 3.25 in that value. I would also not recommend going below 10 seconds for the checkInterval. Otherwise, it's possible to induce a race condition with bittrex.

#### Example file 

```json
{
  "apiKey": "34234898u9rghk",
  "apiSecret": "238ryfiuahskuqh4ri",
  "trade": "BTC",
  "currency": "WAVES",
  "sellValuePercent": 4,
  "buyValuePercent": 7,
  "sellVolumePercent": 3,
  "buyVolumePercent": 3,
  "extCoinBalance": 0,
  "checkInterval": 30,
  "initialSellValue": 0
}
```
__the config file MUST be named botConfig.json__

## Usage
The bot is designed to trade a single token at a time. It's recommended to run it in the docker container. 
Docker will need to be installed prior to trying to run this. To install Docker, see their installation guide:
https://docs.docker.com/engine/installation/ 
The docker image can be found at __jufkes/bittrexBot__

To run:
docker run -d --name <name> -v /path/to/directory_containing_config_file:/opt/bittrexBot/config jufkes/bittrexbot:latest

Example:
docker run -d --name waves -v /opt/botdefs/waves:/opt/bittrexBot/config --restart always jufkes/bittrexbot:latest

-- The waves directory, in this case, contains the botConfig.json

## Utilities
Bots run without your intervention. It is recommended that you have a means to track your trades ergo, track the trades the bot is making for you. That is the same for this bot as well as any other bots you may try.

I track my trades using [CryptoNotify](http://cryptonotify.com). This tool can be setup to email executed trades or, as I prefer, send a message to a Slack channel.

## License
Code released under the [MIT License](https://github.com/jufkes/bittrexBot/master/LICENSE).
