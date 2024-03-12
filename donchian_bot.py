from trade_bot import *
from Data.mexc_data import *
from Data.bybit_data import *

from Indicators.donchian import *

from Strategies.donchian_breakout import *

from more_itertools import chunked

import telegram_bot as tg

import asyncio

from payment_yoomoney import Yoomoney

from time import sleep

from user import User, db_controller

class DonchianBreakoutBot(Trade_Bot, DonchianBreakout_Strategy, tg.Telegram_interface, Yoomoney):

    def __init__(self, name, telegram_token, exchange_token, yoomoney_token, mode='live'):
        
        # --- For trading robot
        self.active = {}
        self.crypto_pairs_data = {}
        self.day = {}
        self.last_breakout = {}

        self.donchian = {}

        # --- Common
        self.markup = None
        super().__init__(name, exchange_token, mode)
        check_sub_thread = threading.Thread(target=self.activate_tg, args=[telegram_token])
        check_sub_thread.daemon = True
        check_sub_thread.start()
        self.yoomoney__init__(token=yoomoney_token)

        self.mexc = Mexc()
        self.bybit = Bybit()
        




    def realize_trade(self, ticker, price_in, time_in, type_in, exchange, type_public, take='', stop='', lots=1):
        
        exchange_text = f"Доступно на {exchange}"
        if exchange=="common":
            exchange_text = "Доступно на MEXC и ByBit"
        for user in self.users:
            if self.users[user].subscription:

                if type_public=="spot":
                    if exchange in self.users[user].tickers_stream_spot or exchange=="common":
                        if type_in=="long":
                            self.bot.send_message(user, text=f"📈 {ticker} {time_in} (utc+0)\nЦена {price_in}\nПробитие максимума цены за 60 дней {self.donchian[ticker][0]}\n\n{exchange_text}")
                        elif type_in=="short":
                            self.bot.send_message(user, text=f"📉 {ticker} {time_in} (utc+0)\nЦена {price_in}\nПробитие минимума цены за 60 дней {self.donchian[ticker][1]}\n\n{exchange_text}")
                elif type_public=="future":
                    if exchange in self.users[user].tickers_stream_future:
                        if type_in=="long":
                            self.bot.send_message(user, text=f"📈 {ticker} {time_in} (utc+0)\nЦена {price_in}\nПробитие максимума цены за 60 дней {self.donchian[ticker][0]}\n\n{exchange_text}")
                        elif type_in=="short":
                            self.bot.send_message(user, text=f"📉 {ticker} {time_in} (utc+0)\nЦена {price_in}\nПробитие минимума цены за 60 дней {self.donchian[ticker][1]}\n\n{exchange_text}")

    def prepare_data(self):

        #MEXC
        crypto_list_spot_mexc = self.mexc.spot_get_rating_by_volume(400)
        crypto_list_contract_mexc = self.mexc.future_get_rating_by_volume(300)

        #Bybit
        crypto_list_spot_bybit = self.bybit.spot_get_ticker_by_volume(400)
        crypto_list_contract_bybit = self.bybit.future_get_ticker_by_volume(300)

        #Comparing
        # --- COMMON ---
            
        self.crypto_pairs_data["common"] = []

        for ticker in crypto_list_spot_mexc:

            if (ticker in crypto_list_spot_mexc) and (ticker in crypto_list_contract_mexc) and (ticker in crypto_list_spot_bybit) and (ticker in crypto_list_contract_bybit):
                self.crypto_pairs_data["common"].append(ticker)

                crypto_list_spot_mexc.remove(ticker)
                crypto_list_contract_mexc.remove(ticker)
                crypto_list_spot_bybit.remove(ticker)
                crypto_list_contract_bybit.remove(ticker)

        for ticker in crypto_list_spot_mexc:

            if (ticker in crypto_list_spot_mexc) and (ticker in crypto_list_spot_bybit):
                self.crypto_pairs_data["common"].append(ticker)
                crypto_list_spot_mexc.remove(ticker)
                crypto_list_spot_bybit.remove(ticker)


        # --- MEXC COMMON ---
                
        self.crypto_pairs_data["mexc_common"] = []

        for ticker in crypto_list_spot_mexc:

            if (ticker in crypto_list_spot_mexc) and (ticker in crypto_list_contract_mexc):
                self.crypto_pairs_data["mexc_common"].append(ticker)

                crypto_list_spot_mexc.remove(ticker)
                crypto_list_contract_mexc.remove(ticker)


        # --- BYBIT COMMON ---
                
        self.crypto_pairs_data["bybit_common"] = []

        for ticker in crypto_list_spot_bybit:

            if (ticker in crypto_list_spot_bybit) and (ticker in crypto_list_contract_bybit):
                self.crypto_pairs_data["bybit_common"].append(ticker)

                crypto_list_spot_bybit.remove(ticker)
                crypto_list_contract_bybit.remove(ticker)

        print("SETS")
        print("COMMON: ", self.crypto_pairs_data["common"])
        print("MEXC COMMON: ", self.crypto_pairs_data["mexc_common"])
        print("BYBIT COMMON: ", self.crypto_pairs_data["bybit_common"])

    def launch_live(self):

        # while True: 

        #     self.prepare_data()
            
        # # ---- LAUNCH ------------
        #     # self.live("MEXC", "spot", crypto_list_spot_mexc)

        #     threads = []

        #     for part in list(chunked(self.crypto_pairs_data["common"], 40)):
        #         thread = threading.Thread(target=self.live, args=["common", "future", "spot", part])
        #         threads.append(thread)

        #     thread = threading.Thread(target=self.live, args=["MEXC", "future", "spot", self.crypto_pairs_data["mexc_common"]])
        #     threads.append(thread)

        #     for part in list(chunked(self.crypto_pairs_data["bybit_common"], 70)):
        #         thread = threading.Thread(target=self.live, args=["ByBit", "future", "spot", part])
        #         threads.append(thread)

        #     for thread in threads:
        #         thread.start()
        #     while threading.active_count() > 1:
        #         for thread in threads:
        #             thread.join(timeout=20)

        #     self.crypto_pairs_data = {}

        #     time.sleep(120)

        self.prepare_data()
            
        # ---- LAUNCH ------------
        # self.live("MEXC", "spot", crypto_list_spot_mexc)

        threads = []

        for part in list(chunked(self.crypto_pairs_data["common"], 40)):
            thread = threading.Thread(target=self.live, args=["common", "future", "spot", part])
            threads.append(thread)

        for part in list(chunked(self.crypto_pairs_data["mexc_common"], 40)):
            thread = threading.Thread(target=self.live, args=["common", "future", "spot", part])
            threads.append(thread)

        # thread = threading.Thread(target=self.live, args=["MEXC", "future", "spot", self.crypto_pairs_data["mexc_common"]])
        # threads.append(thread)

        # for part in list(chunked(self.crypto_pairs_data["bybit_common"], 70)):
        #     thread = threading.Thread(target=self.live, args=["ByBit", "future", "spot", part])
        #     threads.append(thread)

        for thread in threads:
            thread.start()



    def live(self, exchange, type_public, type_, crypto_list):

        while True:

            current_time = datetime.now()

            for symbol in crypto_list:

                print(symbol)


                if exchange=="common":
                    
                    candle_5m = (self.mexc.mexc_get_candles(type_=type_, pair=symbol, interval="5m",from_=datetime.now()-timedelta(minutes=5),till=datetime.now(),limit=2))[-1]
                    day = candle_5m["time"]

                    candles_D = []
                    if (symbol not in self.day) or (current_time > self.day[symbol]+timedelta(hours=6)) or (symbol not in self.donchian):

                        candles_D = (self.mexc.mexc_get_candles(type_=type_, pair=symbol, interval="1d", from_=datetime.now()-timedelta(days=60),till=datetime.now(), limit=60))

                        self.donchian[symbol] = donchian(candles=candles_D)
                        self.day[symbol] = day

                
                elif exchange=="MEXC":
        
                    candle_5m = self.mexc.mexc_get_candles(type_=type_, pair=symbol, interval="5m", from_=datetime.now()-timedelta(minutes=5),till=datetime.now(), limit=2)[-1]
                    day = candle_5m["time"]

                    candles_D = []
                    if (symbol not in self.day) or (current_time > self.day[symbol]+timedelta(hours=6)) or (symbol not in self.donchian):

                        candles_D = (self.mexc.mexc_get_candles(type_=type_, pair=symbol, interval="1d", from_=datetime.now()-timedelta(days=60),till=datetime.now(), limit=60))

                        self.donchian[symbol] = donchian(candles=candles_D)
                        self.day[symbol] = day


                elif exchange=="ByBit":

                    candle_5m = (self.bybit.bybit_get_candles(type_=type_, ticker=symbol, interval="5m", limit=2))[-1]
                    day = candle_5m["time"]

                    candles_D = []
                    if (symbol not in self.day) or (current_time > self.day[symbol]+timedelta(hours=6)) or (symbol not in self.donchian):
                        candles_D = (self.bybit.bybit_get_candles(type_=type_, ticker=symbol, interval="1d", limit=60))[::-1]

                        self.donchian[symbol] = donchian(candles=candles_D)
                        self.day[symbol] = day

                    
                self.entry_trade(ticker=symbol, day=day, candle=candle_5m, candles=candles_D, exchange=exchange, type_public=type_public)

            sleep(60)
