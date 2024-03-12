from Indicators.donchian import *
from Solvings.solvings import *
from datetime import datetime, timedelta

from Data.mexc_data import *

class DonchianBreakout_Strategy():

    def entry_trade(self, ticker, day, candle, candles, exchange, type_public, mode='real'):
        """ticker: BTCUSDT
        day: datetime
        candle: {h l c o v t}
        candles: [{h l c o v t} last 60 days"""
    
        if float(candle["close"])>self.donchian[ticker][0]:

            if ticker not in self.last_breakout or self.last_breakout[ticker] + timedelta(hours=12) < candle["time"]:
                self.last_breakout[ticker] = candle["time"]

                if mode=='real':
                    self.realize_trade(ticker=ticker, price_in=candle["close"], time_in=day.strftime("%Y-%m-%d %H:%M:%S"), type_in='long', exchange=exchange, type_public=type_public)
                elif mode=='test':
                    return {'solution': True, 'type_in': 'long', 'price_in': float(candle["close"]), 'time_in': day.strftime("%Y-%m-%d %H:%M:%S"), 'ticker': ticker}
                
        if float(candle["close"])<self.donchian[ticker][1]:

            if ticker not in self.last_breakout or self.last_breakout[ticker] + timedelta(hours=12) < candle["time"]:
                self.last_breakout[ticker] = candle["time"]

                if mode=='real':
                    self.realize_trade(ticker=ticker, price_in=float(candle["close"]), time_in=day.strftime("%Y-%m-%d %H:%M:%S"), type_in='short', exchange=exchange, type_public=type_public)
                elif mode=='test':
                    return {'solution': True, 'type_in': 'short', 'price_in': float(candle["close"]), 'time_in': day.strftime("%Y-%m-%d %H:%M:%S"), 'ticker': ticker}
                
        if mode=='test':
            return {'solution': False}

        