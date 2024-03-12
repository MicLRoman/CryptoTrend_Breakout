# import websocket
# import threading
# import _thread
# import json

# class SocketConn(websocket.WebSocket):

#     def __init__(self, url, params=[]):
#         super().__init__(self, url, params)

from datetime import datetime, timedelta
import time

import asyncio

import requests

class Mexc():

    base = "https://api.mexc.com"

    spot_info_base = "/api/v3/exchangeInfo"
    spot_candles_base =  "/api/v3/klines"

    contract_base = "https://contract.mexc.com"

    contract_info_base = "/api/v1/contract/ticker"
    contract_candles_base =  "/api/v1/contract/kline/"


    def spot_datetime_to_timestamp(self, time):
        timestamp = time.timestamp()
        decimal_digits = len(str(timestamp).split('.')[1]) if '.' in str(timestamp) else 0
        return int(timestamp*(1000**decimal_digits))
    
    def spot_timestamp_to_datetime(self, time):
        dt_object = datetime.utcfromtimestamp(time/1000)
        return dt_object


    def spot_exchange_info(self):
        return (requests.get(f"{self.base}{self.spot_exchange_info_base}")).json()

    def spot_crypto_get_candles(self, pair, interval, from_='', till='', limit=''):
        link = f"{self.base}{self.spot_candles_base}?symbol={pair}&interval={interval}"
        if from_!='':
            link += f"&startTime={from_}"
        if till!='':
            link += f"&endTime={till}"
        if limit!='':
            link += f"&limit={limit}"

        print(link)
        
        response = 1
        while True:
            try:
                response = requests.get(link)
                result = response.json()
                o = []
                for i in result:
                    o.append(i)
                if len(o)>0:
                    break
                else:
                    time.sleep(10)

            except:
                for id in self.developers_id:

                    self.bot(id, "!!! НЕ УСПЕШНЫЙ ЗАПРОС !!!")
                print("ovvovofnvondvodvndov")
                time.sleep(10)

        
        return result
    
    def spot_get_rating_by_volume(self, limit):

        response = requests.get(f"{self.base}/api/v3/ticker/24hr")
        data = response.json()

        sorted_tickers = []
        for ticker in data:
            if "USDT" in ticker["symbol"]:
                sorted_tickers.append(
                    (ticker["symbol"], float(ticker["quoteVolume"]))
                    )
        sorted_tickers.sort(key=lambda x: x[1], reverse=True)

        tickers = []
        for i in range(0, limit):
            tickers.append(sorted_tickers[i][0])

        return tickers
    



    def future_datetime_to_timestamp(self, time_):
        timestamp = time_.timestamp()
        milliseconds = int(round(timestamp))
        return milliseconds
    
    def future_timestamp_to_datetime(self, time):
        dt_object = datetime.utcfromtimestamp(time)
        return dt_object


    def future_get_all_pairs(self):
        return (requests.get(f"{self.contract_base}{self.contract_info_base}")).json()
    
    

    def future_crypto_get_candles(self, pair, interval, from_='', till=''):
        link = f"{self.contract_base}{self.contract_candles_base}{pair}?interval={interval}"
        if from_!='':
            link += f"&start={from_}"
        if till!='':
            link += f"&end={till}"
        print(link)
        response = 1
        while response==1:
            try:
                response = requests.get(link)
            except:
                time.sleep(10)

        result = response.json()
        return result
    
    def future_get_rating_by_volume(self, limit):

        data = self.future_get_all_pairs()
        sorted_tickers = []
        for ticker in data["data"]:
            if "USDT" in ticker["symbol"]:
                sorted_tickers.append((ticker["symbol"].replace("_", ""), ticker["amount24"]))
        sorted_tickers.sort(key=lambda x: x[1], reverse=True)
        
        tickers = []
        for i in range(0, limit):
            tickers.append(sorted_tickers[i][0])

        return tickers
    

    def mexc_get_candles(self, type_, pair, interval, from_, till, limit):

        candles = []

        if type_=="spot":

            candles_mexc_format = self.spot_crypto_get_candles(pair=pair, interval=interval, limit=limit)
            for candle in candles_mexc_format:
                candles.append({"open": candle[1], "high": candle[2], "low": candle[3], "close": candle[4], "volume": candle[7], "time": self.spot_timestamp_to_datetime(time=candle[0])})
        
        elif type_=="contract":
            if interval=='1m':
                interval = 'Min1'
            elif interval=='5m':
                interval = 'Min5'
            elif interval=='1d':
                interval = "Day1"
            candle_mexc_format = self.future_crypto_get_candles(pair=pair,interval=interval, from_=bot.future_datetime_to_timestamp(time_=from_), till=bot.future_datetime_to_timestamp(time_=till))
            for index in range(0, len(candle_mexc_format["data"]["time"])):
                candles.append(
                    {"open": candle_mexc_format["data"]["open"][index], 
                     "high": candle_mexc_format["data"]["high"][index], 
                     "low": candle_mexc_format["data"]["low"][index], 
                     "close": candle_mexc_format["data"]["close"][index], 
                     "volume": candle_mexc_format["data"]["amount"][index], 
                     "time": self.spot_timestamp_to_datetime(time=candle_mexc_format["data"]["time"][index])}
                     )
                
        return candles
                

            
        







if __name__ == "__main__":

    bot = Mexc()
    print(bot.spot_crypto_get_candles(pair="BTCUSDT", interval="1d", limit=61))


