from telebot import TeleBot, types
from datetime import datetime, timedelta
from random import choice
from string import ascii_letters

from __main__ import *

from Database.db_controller import *
db_controller = Controller(db_name="DonchianBot_DB")

class User():

    def __init__(self, bot, username, id):
        self.bot = bot
        self.name = username
        self.chat_id = id
        self.subscription = False
        self.date_of_end = ''

        self.limit = False

        self.tickers_stream_spot = ["common"]  #{type (spot or future): exchange}
        self.tickers_stream_future = ["common", "MEXC", "ByBit"]
        self.discount_rub = 0
        self.discount_percent = 0
        self.inviter_referral_code_activated = False     #defult: False or inviter_id
        self.user_referral_code = "".join(choice(ascii_letters) for _ in range(8))  #code
        self.referral_code_activated = False

 
        try:
            data = db_controller.get_user_with_sub_by_chat_id(chat_id=self.chat_id)
            if data != {}:
                self.discount = data["Discount"]
                if data["Subscription"]==1:
                    self.subscription = True
                if self.subscription:
                    self.date_of_end = data["DateOfEnd"]
                    if datetime.strptime(self.date_of_end, "%Y-%m-%d %H:%M:%S")>datetime.now()+timedelta(days=365*10):
                        self.limit = True

            else:
                #Add new user
                db_controller.add_user_with_sub(chat_id=self.chat_id, subscription=self.subscription, date_of_end='', sender_username=self.name, discount=0)
        except: 
            ''

    def apply_payment(self, type_):

        self.subscription = True

        if type_=="buy_7days":
            if self.date_of_end=='':
                now = datetime.now()
                self.date_of_end = (datetime(year=now.year, month=now.month, day=now.day, hour=now.hour, minute=now.minute, second=now.second)+timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
                self.bot.send_message(self.chat_id, f"Поздравляю с приобретением! Теперь у вас есть подписка до {self.date_of_end}")
            else:
                now = datetime.strptime(self.date_of_end, "%Y-%m-%d %H:%M:%S")
                self.date_of_end = (datetime(year=now.year, month=now.month, day=now.day, hour=now.hour, minute=now.minute, second=now.second)+timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
            return
        
        if type_=="buy_month":
            add_month = 1
        elif type_=="buy_3monthes":
            add_month = 3
        elif type_=="buy_6monthes":
            add_month = 6
        elif type_=="buy_12monthes":
            add_month = 12
        elif type_=="buy_nolimit":
            add_month = 9999
            self.limit = True

        if self.date_of_end=='':
            now = datetime.now()
            self.date_of_end = datetime(year=now.year+(now.month+add_month)//12, month=(now.month+add_month)%12, day=now.day, hour=now.hour, minute=now.minute, second=now.second).strftime("%Y-%m-%d %H:%M:%S")
        else:
            now = datetime.strptime(self.date_of_end, "%Y-%m-%d %H:%M:%S")
            self.date_of_end = datetime(year=now.year+(now.month+add_month)//12, month=(now.month+add_month)%12, day=now.day, hour=now.hour, minute=now.minute, second=now.second).strftime("%Y-%m-%d %H:%M:%S")

        #To db
        db_controller.update_dateofend_of_subscription_of_user_with_sub(chat_id=self.chat_id, data=self.date_of_end)
        db_controller.update_subscription_of_user_with_sub(chat_id=self.chat_id, data=1)

        try:
            if self.limit == True:
                self.bot.send_message(self.chat_id, f"Поздравляю с покупкой! Теперь у вас неграниченная подписка")
            else:
                self.bot.send_message(self.chat_id, f"Поздравляю с покупкой! Теперь у вас есть подписка до {self.date_of_end}")
        except:
            ''


    def stop_subscription(self):

        self.subscription = True
        self.date_of_end = ''
        
        #To db
        db_controller.update_dateofend_of_subscription_of_user_with_sub(chat_id=self.chat_id, data=self.date_of_end)
        db_controller.update_subscription_of_user_with_sub(chat_id=self.chat_id, data=1)

    def payment_cancel(self):

        self.bot.send_message(self.chat_id, "Покупка была отменена.")

    def user_discount_activated(self, sum_, activated_user):
        self.discount_rub = sum_
        self.bot.send_message(self.chat_id, f"Пользователь {activated_user} воспользовался вашим реферальным кодом и купил подписку! Вы получаете скидку на следующую покупку: {sum_} рублей")


    def dev_get_all_ids(self):
        return db_controller.get_all_user_ids()


