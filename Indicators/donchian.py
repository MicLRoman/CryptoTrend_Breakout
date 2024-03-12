from  Indicators.atr import *

def donchian(candles, period=60):

    if len(candles)<period:
        period=len(candles)

    "{high close low high}"

    high_band = 0
    low_band = 1000000000000000000000000000000000000000000000000000000000
    for candle in candles[-(period):]:

        high = float(candle["high"])
        if high>high_band:
            high_band = high

        low = float(candle["low"])
        if low<low_band:
            low_band = low

    return (high_band, low_band)



    