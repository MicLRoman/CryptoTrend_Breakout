from telebot import TeleBot, types
import threading
from time import sleep
from datetime import datetime

from user import User, db_controller

class Telegram_interface():

    def activate_tg(self, token):

        self.reply_blacklist = []

        self.users = {}                     #{user_id: User(class)}
        self.users_promocode = {}           #{code: user_id}
        self.origin_referral_code = 'ZEROCODE'
        self.main_button = "ㅤ📲Menuㅤ"

        self.subscription_price = {"buy_month": 1990, "buy_3monthes": 5390, "buy_6monthes": 9590, "buy_12monthes": 16990, "buy_nolimit": 69990} #1990 5390 9590 16990 69990

        self.bot = TeleBot(token)

        self.prepare()

        self.bot.infinity_polling(timeout=500)
        




    def prepare(self):
        #Create menu markup
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        markup.add(types.KeyboardButton(self.main_button))
        self.markup = markup

        # #Add developers
        # for id in self.developers_id:
        #     if not db_controller.check_the_existing_of_user(chat_id=id):
        #         self.users[id] = User(bot=self.bot, username='', id=id)
        #         self.users_promocode[self.users[id].user_referral_code] = id
        #         self.users[id].apply_payment(type_="buy_nolimit")
                

        #Check the subscription each hour
        check_sub_thread = threading.Thread(target=self.check_subscripion)
        check_sub_thread.daemon = True
        check_sub_thread.start()

    # --- Telegram Commands ---------------------------------------
        @self.bot.message_handler(commands=["start"])
        def start_message(message):

            if message.chat.id not in self.users:
                self.users[message.chat.id] = User(bot=self.bot, username=message.from_user.username, id=message.chat.id)
                self.users_promocode[self.users[message.chat.id].user_referral_code] = message.chat.id
            
            self.bot.send_message(message.chat.id, """⚡️ CryptoTrend Notification Bot —  универсальный бот-шпион, который вместо вас следит за рынком и присылает моментальные уведомления об изменениях на бирже.

С подпиской на бота вы сможете:

📈 Получать моментальные уведомления по стратегии прорыва тренда Дончиана. Максимума и минимума за 60 дней
🎯 Работать с криптовалютами бирж Bybit и MEXC
⚙️ Остальные преимущества в разработке...

Обратите также внимание на нашу реферальную систему. Где по коду, который вам отправит наш пользователь, вы получите на выбор:

✅ Скидку в 10% на следующую оплату бота
✅ Бесплатный 7 дневный период

А если по вашему коду вы пригласите своих друзей, то вы получите скидку в 10% от стоимости их подписки🔥""", reply_markup=self.markup)
            
        
            

        @self.bot.message_handler(commands=["referral"])
        def referral(message):

            if not self.users[message.chat.id].inviter_referral_code_activated:
                referral_text = "\n\nЧтобы активировать промокод нажмите на кнопку ниже!"
            
            markup = types.InlineKeyboardMarkup()
            button1 = types.InlineKeyboardButton(
                text="Активировать промокод",
                callback_data="activate_promocode",
            )
            markup.add(button1)
            self.bot.send_message(message.chat.id, f"Ваш код: `{self.users[message.chat.id].user_referral_code}`\n\nВы можете поделиться вашим кодом! Тогда тот, кто его использует получит:\n - На выбор: 10% на следующую покупку ИЛИ 7 дней пробного периода.\nВы же получите 10% скидки от суммы того человека, который воспользовался вашим кодом!{referral_text}", parse_mode="Markdown", reply_markup=markup)


        def tariffes(message):
            markup = types.InlineKeyboardMarkup()
            button1 = types.InlineKeyboardButton(
                text="1 месяц - 1 990 рублей",
                callback_data="buy_month",
            )
            markup.add(button1)
            button1 = types.InlineKeyboardButton(
                text="3 месяца - 5 390 рублей (выгода 10%)",
                callback_data="buy_3monthes",
            )
            markup.add(button1)
            button1 = types.InlineKeyboardButton(
                text="6 месяцев - 9 590 рублей (выгода 20%)",
                callback_data="buy_6monthes",
            )
            markup.add(button1)
            button1 = types.InlineKeyboardButton(
                text="12 месяцев - 16 990 рублей (выгода 30%)",
                callback_data="buy_12monthes",
            )
            markup.add(button1)
            button1 = types.InlineKeyboardButton(
                text="Безлимитная подписка - 69 990 рублей (выгода - бесценно)",
                callback_data="buy_nolimit",
            )
            markup.add(button1)

            self.bot.send_message(message.chat.id, """Тариф "Все включено" - ниже представлены планы""", reply_markup=markup)


        def buy_subscription(type_, message):

            cost = self.subscription_price[type_]
# -------------------DISCOUNT-------------------------
            #%
            cost = round(cost*(1-self.users[message.chat.id].discount_percent), 0)
            print(cost)
            #rub
            cost = cost - self.users[message.chat.id].discount_rub

            if cost<2:
                self.users[message.chat.id].apply_payment(type_=type_)
                return

            form = self.create_form(cost=cost)

            markup = types.InlineKeyboardMarkup()
            button1 = types.InlineKeyboardButton(
                text="Перейти к оплате",
                url=form.redirected_url,
            )
            markup.add(button1)


            self.bot.send_message(message.chat.id, f"К оплате {cost} рублей.\n\nОплата будет отменена через 5 минут.", reply_markup=markup)
            
            payment_thread = threading.Thread(target=self.accept_payment, args=[form.label, message.chat.id, type_, self.subscription_price[type_]])
            payment_thread.daemon = True
            payment_thread.start()

        #Referral
        def activate_promocode_reply_handler(inner_message):
            if inner_message.text in self.users_promocode and inner_message.text!=self.users[inner_message.chat.id].user_referral_code:
                self.users[inner_message.chat.id].inviter_referral_code_activated = self.users_promocode[inner_message.text]
                markup = types.InlineKeyboardMarkup()
                button1 = types.InlineKeyboardButton(
                    text="7 дней пробной подписки",
                    callback_data="promocode_7days",
                )
                markup.add(button1)
                button1 = types.InlineKeyboardButton(
                    text="10% скидка на следующую покупку",
                    callback_data="promocode_percent",
                )
                markup.add(button1)
                self.bot.send_message(inner_message.chat.id, "Выбери себе привелегию:", reply_markup=markup)
            elif inner_message.text == self.origin_referral_code:
                self.users[inner_message.chat.id].inviter_referral_code_activated = True
                self.bot.send_message(inner_message.chat.id, "Промокод активирован.")
                self.users[inner_message.chat.id].apply_payment(type_="buy_7days")
            else:
                self.bot.send_message(inner_message.chat.id, "...Введен неверный промокод...")
        def activate_promocode(message):
            bot_reply = self.bot.reply_to(message, "Напишите в ответ на это сообщение ваш промокод")
            self.reply_blacklist.append(bot_reply.message_id)
            self.bot.register_for_reply(bot_reply, activate_promocode_reply_handler)
        def apply_percent_promocode(message):
            if self.users[message.chat.id].referral_code_activated == False:
                self.users[message.chat.id].referral_code_activated = True
                self.users[message.chat.id].discount_percent = 0.1
                self.bot.send_message(message.chat.id, "Промокод активирован. Теперь у вас 10% скидки на следующую покупку.")
        def apply_7_days_sub_promocode(message):
            if self.users[message.chat.id].referral_code_activated == False:
                self.users[message.chat.id].referral_code_activated = True
                self.bot.send_message(message.chat.id, "Промокод активирован.")
                self.users[message.chat.id].apply_payment(type_="buy_7days")
        
        def notify_filter(message):

            if not self.users[message.chat.id].subscription:
                self.bot.send_message(message.chat.id, text="Чтобы получать уведомление вам нужно купить подписку")
                return 
            
            customization_markup = types.InlineKeyboardMarkup()

            # --- Buttons ---
            smile = "✅"
            if "common" not in self.users[message.chat.id].tickers_stream_spot:
                smile = "❌"
            button = types.InlineKeyboardButton(
                text="{smile} Споты во всех биржах".format(smile=smile),
                callback_data="switch_to-spot-common",
            )
            customization_markup.add(button)
            smile = "✅"
            # if "MEXC" not in self.users[message.chat.id].tickers_stream_spot:
            #     smile = "❌"
            # button = types.InlineKeyboardButton(
            #     text="{smile} Споты в MEXC".format(smile=smile),
            #     callback_data="switch_to-spot-MEXC",
            # )
            # customization_markup.add(button)
            # smile = "✅"
            # if "ByBit" not in self.users[message.chat.id].tickers_stream_spot:
            #     smile = "❌"
            # button = types.InlineKeyboardButton(
            #     text="{smile} Споты в ByBit".format(smile=smile),
            #     callback_data="switch_to-spot-ByBit",
            # )
            # customization_markup.add(button)
            
            smile = "✅"
            if "common" not in self.users[message.chat.id].tickers_stream_future:
                smile = "❌"
            button = types.InlineKeyboardButton(
                text="{smile} Деривативы во всех биржах".format(smile=smile),
                callback_data="switch_to-future-common",
            )
            customization_markup.add(button)
            smile = "✅"
            if "MEXC" not in self.users[message.chat.id].tickers_stream_future:
                smile = "❌"
            button = types.InlineKeyboardButton(
                text="{smile} Деривативы в MEXC".format(smile=smile),
                callback_data="switch_to-future-MEXC",
            )
            customization_markup.add(button)
            smile = "✅"
            if "ByBit" not in self.users[message.chat.id].tickers_stream_future:
                smile = "❌"
            button = types.InlineKeyboardButton(
                text="{smile} Деривативы в Bybit".format(smile=smile),
                callback_data="switch_to-future-ByBit",
            )
            customization_markup.add(button)

            try:
                self.bot.edit_message_text(
                    "Выберете инструменты, по которым вы хотите получать уведомления",
                    message.chat.id,
                    message.message_id,
                    reply_markup=customization_markup,
                    parse_mode="HTML",
                )
            except:
                ''
        def switch_to(message ,type_, exchange):
            
            if type_=="future":
                if exchange not in self.users[message.chat.id].tickers_stream_future:
                    self.users[message.chat.id].tickers_stream_future.append(exchange)
                else:
                    self.users[message.chat.id].tickers_stream_future.remove(exchange)
            elif type_=="spot":
                if exchange not in self.users[message.chat.id].tickers_stream_spot:
                    self.users[message.chat.id].tickers_stream_spot.append(exchange)
                else:
                    self.users[message.chat.id].tickers_stream_spot.remove(exchange)

            notify_filter(message)

        

        def dev_get_donchian_values(message):
            text = ""
            for ticker in self.donchian:
                text+=f"{ticker}  -->  {self.donchian[ticker]}\n"
            self.bot.send_message(chat_id=message.chat.id, text=text) 
        def dev_create_promocode_reply_handler(inner_message):
            self.origin_referral_code = inner_message.text
            self.bot.send_message(chat_id=inner_message.chat.id, text=f"Новый Нулевой промокод: {self.origin_referral_code}") 
        def dev_create_promocode(message):
            bot_reply = self.bot.reply_to(message, "Напишите в ответ на это сообщение новый промокод")
            self.reply_blacklist.append(bot_reply.message_id)
            self.bot.register_for_reply(bot_reply, dev_create_promocode_reply_handler)
        def dev_send_newletter(message):
            ids = self.users[message.chat.id].dev_get_all_ids()
            for id_ in ids:
                try:
                    self.bot.send_message(id_, message.text)
                except:
                    ''
        def dev_activate_newletter(message):
            bot_reply = self.bot.reply_to(message, "Напишите в ответ на это сообщение ваш текст для рассылки")
            self.reply_blacklist.append(bot_reply.message_id)
            self.bot.register_for_reply(bot_reply, dev_send_newletter)
        

            
            


        @self.bot.callback_query_handler(func=lambda call: True)
        def keyboard_buttons_handler(call):

            if call.message.chat.id not in self.users:
                self.users[call.message.chat.id] = User(bot=self.bot, username=call.message.from_user.username, id=call.message.chat.id)
                self.users_promocode[self.users[call.message.chat.id].user_referral_code] = call.message.chat.id

            call_data = call.data

            if call_data=="about":
                start_message(message=call.message) 
            elif call_data=="referral":
                referral(message=call.message) 

            elif call_data=="notity_filter":
                notify_filter(message=call.message)
            elif call_data.split("-")[0] == "switch_to":
                switch_to(message=call.message, type_=call_data.split("-")[1], exchange=call_data.split("-")[2])

            elif call_data=="buy_subscription":
                tariffes(message=call.message)

            elif call_data=="buy_month" or call_data=="buy_3monthes" or call_data=="buy_6monthes" or call_data=="buy_12monthes" or call_data=="buy_nolimit":
                buy_subscription(type_=call_data, message=call.message)

            elif call_data=="activate_promocode":
                activate_promocode(message=call.message)
            elif call_data=="promocode_7days":
                apply_7_days_sub_promocode(message=call.message)
            elif call_data=="promocode_percent":
                apply_percent_promocode(message=call.message)

            elif call_data=="dev_get_donchian_values":
                dev_get_donchian_values(message=call.message)
            elif call_data=="dev_create_promocode":
                dev_create_promocode(message=call.message)
            elif call_data=="dev_show_promocode":
                self.bot.send_message(chat_id=call.message.chat.id, text=f"Нулевой промокод: {self.origin_referral_code}")
            elif call_data=="dev_newletter":
                dev_activate_newletter(message=call.message)

        @self.bot.message_handler(commands=["dev_tools"])
        def dev_tools(message):

            if message.chat.id not in self.developers_id:
                self.bot.send_message(message.chat.id, "...нет прав...")
                return
                
            markup = types.InlineKeyboardMarkup()
            button1 = types.InlineKeyboardButton(
                text="Получить нулевой код",
                callback_data="dev_show_promocode",
            )
            markup.add(button1)
            button1 = types.InlineKeyboardButton(
                text="Сгенерировать новый нулевой код",
                callback_data="dev_create_promocode",
            )
            markup.add(button1)
            button1 = types.InlineKeyboardButton(
                text="Сделать рассылку",
                callback_data="dev_newletter",
            )
            markup.add(button1)
            
            self.bot.send_message(message.chat.id, "Здесь возможности только для админов", reply_markup=markup)

        def menu(message):
            markup = types.InlineKeyboardMarkup()

            #subscription
            if self.users[message.chat.id].subscription == True and self.users[message.chat.id].limit==True:
                sub_text = f"Вы подписаны на бота. Подписка неограниченна"
                button1 = types.InlineKeyboardButton(
                    text="Поддержать покупкой подписки",
                    callback_data="buy_subscription",
                )
                markup.add(button1)
            elif self.users[message.chat.id].subscription == True:
                sub_text = f"Вы подписаны на бота. Подписка действует до {self.users[message.chat.id].date_of_end}"
                button1 = types.InlineKeyboardButton(
                    text="Продлить подписку",
                    callback_data="buy_subscription",
                )
                markup.add(button1)
            else:
                button1 = types.InlineKeyboardButton(
                    text="Купить подписку",
                    callback_data="buy_subscription",
                )
                markup.add(button1)
                sub_text = f"Подписки на бота нет. Купить её можно ниже!"


            #referral
            referral_text = ''
            if not self.users[message.chat.id].inviter_referral_code_activated:
                referral_text = "\n\nВы можете активировать промокод! Для этого перейдите во вкладку Реферальная програма"
            button1 = types.InlineKeyboardButton(
                text="Реферальная программа",
                callback_data="referral",
            )
            markup.add(button1)

            button1 = types.InlineKeyboardButton(
                text="Настроить уведомление",
                callback_data="notity_filter",
            )
            markup.add(button1)

            button1 = types.InlineKeyboardButton(
                text="О Боте",
                callback_data="about",
            )
            markup.add(button1)

            self.bot.send_message(message.chat.id, text=f"Добро пожаловать в меню!\n\n{sub_text}{referral_text}", reply_markup=markup)

        
        @self.bot.message_handler(func=lambda message: True)
        def echo_all(message):

            if message.chat.id not in self.users:
                self.users[message.chat.id] = User(bot=self.bot, username=message.from_user.username, id=message.chat.id)
                self.users_promocode[self.users[message.chat.id].user_referral_code] = message.chat.id

            if message.reply_to_message != None:
                if message.reply_to_message.message_id in self.reply_blacklist:
                    return

            if message.text == self.main_button:
                menu(message=message)
                return


            self.bot.reply_to(message, "Я работаю, как увижу прорыв, сообщу)", reply_markup=self.markup)

    def check_subscripion(self):

        while True:
            for user in self.users:

                if self.users[user].date_of_end!='': 
                    if datetime.now()>datetime.strptime(self.users[user].date_of_end, "%Y-%m-%d %H:%M:%S"):
                        self.users[user].stop_subscription()

                    #REMINDERS

            sleep(3600)
