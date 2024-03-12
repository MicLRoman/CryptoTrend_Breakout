from datetime import datetime, timedelta
import time

import requests

class Bybit():

    base = "https://api.bybit.com"
    tickers = "/v5/market/tickers"
    candles = "/v5/market/kline"

    def spot_datetime_to_timestamp(self, time):
        timestamp = time.timestamp()
        decimal_digits = len(str(timestamp).split('.')[1]) if '.' in str(timestamp) else 0
        return int(timestamp*(1000**decimal_digits))
    
    def spot_timestamp_to_datetime(self, time):
        dt_object = datetime.utcfromtimestamp(time/1000)
        return dt_object 

    def spot_get_tickers(self):
        return (requests.get(f"{self.base}{self.tickers}?category=spot")).json()
    
    def spot_get_ticker_by_volume(self, limit):

        tickers_bybit_format = self.spot_get_tickers()     #449 tickers
        sorted_tickers = []
        for ticker in tickers_bybit_format["result"]["list"]:
            if "USDT" in ticker["symbol"]:
                sorted_tickers.append((ticker["symbol"],float(ticker["turnover24h"])))
        sorted_tickers.sort(key=lambda x: x[1], reverse=True)

        tickers = []
        for i in range(0, limit):
            tickers.append(sorted_tickers[i][0])

        return tickers
    
    def spot_get_candles(self, ticker, interval, from_='', till='', limit=''):
        response = f"{self.base}{self.candles}?category=spot&symbol={ticker}&interval={interval}"       #5 or D
        if from_!='':
            response = response + f"&start={from_}"
        if till!='':
            response = response + f"&end={till}"
        if limit!='':
            response = response + f"&limit={limit}"

        while True:

            try:
                response = requests.get(response)
                if response:
                    break
            except:
                print("EXCEEEPPPTTT")
                time.sleep(5)
        result = response.json()
        return result
    

    def future_get_tickers(self):
        return (requests.get(f"{self.base}{self.tickers}?category=linear")).json()
    
    def future_get_ticker_by_volume(self, limit):

        tickers_bybit_format = self.spot_get_tickers()     #449 tickers
        sorted_tickers = []
        for ticker in tickers_bybit_format["result"]["list"]:
            if "USDT" in ticker["symbol"]:
                sorted_tickers.append((ticker["symbol"],float(ticker["turnover24h"])))
        sorted_tickers.sort(key=lambda x: x[1], reverse=True)

        tickers = []
        for i in range(0, limit):
            tickers.append(sorted_tickers[i][0])

        return tickers
    
    def future_get_candles(self, ticker, interval, from_='', till='', limit=''):
        response = f"{self.base}{self.candles}?category=linear&symbol={ticker}&interval={interval}"       #5 or D
        if from_!='':
            response = response + f"&start={from_}"
        if till!='':
            response = response + f"&end={till}"
        if limit!='':
            response = response + f"&limit={limit}"

        response = requests.get(response)
        result = response.json()
        return result
    
    def bybit_get_candles(self, type_, ticker, interval, from_='', till='', limit=''):

        candles = []

        if type_=='spot':
            
            if interval=="1m":
                interval = "1"
            elif interval=='5m':
                interval = '5'
            elif interval=='1d':
                interval = 'D'
            bybit_candles = self.spot_get_candles(ticker=ticker, interval=interval, limit=limit)

            for candle in bybit_candles["result"]["list"]:
                candles.append({"open": candle[1], "high": candle[2], "low": candle[3], "close": candle[4], "volume": candle[6], "time": self.spot_timestamp_to_datetime(time=int(candle[0]))})

        elif type_=='contract':
            if interval=='5m':
                interval = '5'
            elif interval=='1d':
                interval = 'D'
            self.future_get_candles(ticker=ticker, interval=interval, limit=limit)

            for candle in bybit_candles["result"]["list"]:
                candles.append({"open": candle[1], "high": candle[2], "low": candle[3], "close": candle[4], "volume": candle[6], "time": self.spot_timestamp_to_datetime(time=int(candle[0]))})

        return candles

if __name__ == "__main__":
    bot = Bybit()
    # print(bot.spot_get_ticker_by_volume(60))

    # print(bot.spot_get_candles(ticker='BTCUSDT', interval='5', limit=1))

    print(bot.spot_get_candles(ticker='BABYDOGEUSDT', interval='D', limit=60))