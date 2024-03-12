from atr import ATR

def last_supertrend(candles, multiplier):

    high = candles[-1]["high"]
    low = candles[-1]["low"]

    hl2 = (high + low) / 2

    #Bands
    basicUpperBand = hl2 + (multiplier * ATR(candles=candles))
    basicLowerBand = hl2 - (multiplier * ATR(candles=candles))

    #Trend
    if candles["close"] > basicUpperBand:
        trend = "up"
        supertrend = basicUpperBand
    elif candles["close"] < basicLowerBand:
        trend = "down"
        supertrend = basicLowerBand
    
    return {"trend" :trend, "value": supertrend}

def supertrend_with_breaks(candles, multiplier):

    # --- Actual candle value --------------------

    high = candles[-1]["high"]
    low = candles[-1]["low"]

    hl2 = (high + low) / 2

    #Bands
    basicUpperBand = hl2 + (multiplier * ATR(candles=candles))
    basicLowerBand = hl2 - (multiplier * ATR(candles=candles))

    #Trend
    if candles["close"] > basicUpperBand:
        trend = "up"
        supertrend = basicUpperBand
    elif candles["close"] < basicLowerBand:
        trend = "down"
        supertrend = basicLowerBand

    
    # --- Prev candle value -------------------------

    prev_high = candles[-2]["high"]
    prev_low = candles[-2]["low"]

    prev_hl2 = (prev_high + prev_low) / 2

    #Bands
    basicUpperBand = prev_hl2 + (multiplier * ATR(candles=candles[:-1]))
    basicLowerBand = prev_hl2 - (multiplier * ATR(candles=candles[:-1]))

    #Trend
    if candles["close"] > basicUpperBand:
        prev_trend = "up"
        prev_supertrend = basicUpperBand
    elif candles["close"] < basicLowerBand:
        prev_trend = "down"
        prev_supertrend = basicLowerBand


    breakout = False
    if prev_trend!=trend:
        breakout = True
    
    return {"trend": trend, "value": supertrend, "breakout": breakout}


def supertrends_in_period(candles, multiplier, period):

    "Later"