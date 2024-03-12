def ema(data, period, alpha):
    """
    Расчёт скользящей средней экспоненциальной.

    Args:
        data: Список значений.
        period: Период скользящей средней.
        alpha: Коэффициент сглаживания.

    Returns:
        Список значений скользящей средней.
    """

    ema = [0] * len(data)
    for i in range(len(data)):
        if i < period:
            ema[i] = data[i]
        else:
            ema[i] = (ema[i - 1] * (1 - alpha) + data[i] * alpha)
    return ema

def ma(data, period):
    # print(data)
    # print(data[-period:])
    return sum(data[-period:])/len(data[-period:])