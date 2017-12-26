import requests

RESULT = "result"
MARKET_NAME = "MarketName"
BTC_PREFIX = "BTC"


class BittrexService:
    market_request = "https://bittrex.com/api/v1.1/public/getmarketsummaries"

    def fetch_btc_coin_data(self):
        return requests.get(self.market_request).json()

    def fetch_active_btc_pairs(self):
        coin_list = []
        coin_data = self.fetch_btc_coin_data()
        print(coin_data)
        for coin in coin_data[RESULT]:
            if str(coin[MARKET_NAME]).startswith(BTC_PREFIX):
                coin_list.append(coin[MARKET_NAME])

        return coin_list
