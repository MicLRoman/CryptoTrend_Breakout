

def ATR(candles, range_=7):

    tr = []
    for i in range(1, range_+1):
        tr.append(TR(candle=candles[-i], prev_candle=candles[-(i+1)]))

    atr = sum(tr) / len(tr)

    return atr


def TR(candle, prev_candle):

    high = candle["high"]
    low = candle["low"]
    close_prev = prev_candle["close"]
    
    atr1 = float(high) - float(low)
    atr2 = float(high) - float(close_prev)
    atr3 = float(low) - float(close_prev)

    res = max(atr1, atr2, atr3)

    return res