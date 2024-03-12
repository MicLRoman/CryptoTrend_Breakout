"""Bot checks the abnormal volume on 5M candles"""

from os import environ, path, makedirs
import threading
import pandas as pd

from telebot import TeleBot, types

class Trade_Bot():

    active_trades = []  #pandas{ticker: [str], type_trade: ['long'or'short'], price_in: [float], lots: [int], time_in: [yyyy-mm-dd hh-mm-ss], take: [float], stop: [float]}
    ended_trades = []   #{ticker: [str], type_trade: ['long'or'short'], price_in: [float], lots: [int], time_in: [yyyy-mm-dd hh-mm-ss], price_out: [float], time_out:[ yyyy-mm-dd hh-mm-ss]}

    def __init__(self, name, exchange_token, mode='live'): 

        self.name = name

        if mode=='test':
            return

        self.users_to_notify = [1803492306, 779855407]
        self.developers_id = [1803492306]
        
        self.exchange_token = exchange_token

        # --- Telegram API ---
        


        # --- local_interaction ---

    def end_trade(self, active_trade, price_out, time_out):
        
        self.active_trades.remove(active_trade)

        active_trade["price_out"] = price_out
        active_trade["time_out"] = time_out

        self.ended_trades.append(active_trade)

    def change_active_trade(self, active_trade, new):  #new - [name_of_column, new_value]
        self.active_trades[new[0]] = new[1]

        
        
if __name__ == '__main__':
    bot = Trade_Bot(name="VolumeBot", strategies="abnormal_volume", tinkoff_token='tinkoff_token')
    while True:
        p = 7
