from os import environ
from dotenv import load_dotenv

import asyncio

load_dotenv(".env")

# telegram_token = environ.get("TELEGRAM_TOKEN_DONCHIAN")
telegram_token = environ.get("TELEGRAM_TOKEN_DONCHIAN_TEST")
if not telegram_token:
    raise Exception
payment_token = environ.get("YOOMONEY_TOKEN")
if not payment_token:
    raise Exception

from donchian_bot import *
bot = DonchianBreakoutBot(name="DonchianBot", telegram_token=telegram_token, exchange_token='', yoomoney_token=payment_token)

bot.launch_live()
# bot.backtest_launch_live()

#SERVER
# 31.129.51.176
# root
# 8Ne580LlVRuq