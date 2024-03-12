from __main__ import *
import threading
import time
import random
from yoomoney import Client
from yoomoney import Quickpay



class Yoomoney():

    def yoomoney__init__(self, token):
        self.yoomoney_token = token
        self.yoomoney_client = Client(token)

    def accept_payment(self, label, id, type_, cost, timeout=240.0):
        result = [
            None
        ]  # используем список вместо прямого значения, чтобы иметь возможность изменить его в любом потоке

        def check_payment(label):
            # Проверяем историю операции
            try:
                history = self.yoomoney_client.operation_history(label=label)

                for operation in history.operations:
                    if operation.status == "success":
                        result[0] = True
                    else:
                        result[0] = False
            except:
                result[0] = False

        start_time = time.time()

        # Запускаем таймеры, пока не истечет общее время ожидания
        while time.time() - start_time < timeout and result[0] is None:
            timer = threading.Timer(20.0, lambda: check_payment(label))
            timer.start()
            timer.join()

        if result[0] is None:
            result[0] = False

        if result[0]:
            #Referral
            if self.users[id].inviter_referral_code_activated!=False or self.users[id].inviter_referral_code_activated!=True:
                self.users[self.users[id].inviter_referral_code_activated].user_discount_activated(sum_=cost, activated_user=self.users[self.users[id].inviter_referral_code_activated].name)
                self.users[id].inviter_referral_code_activated = True

            return self.users[id].apply_payment(type_=type_)
        else:
            # return self.users[id].apply_payment(type_=type_)
            return self.users[id].payment_cancel()


    def create_form(self, cost):
        # Генерация случайного 8-значного числа для label
        label = random.randint(10000000, 99999999)

        # Создание формы оплаты
        quickpay = Quickpay(
            receiver="4100118270605528",
            quickpay_form="shop",
            targets="Buy product",
            paymentType="SB",
            sum=cost,  # cost
            label=label,
        )

        return quickpay

        # # Вызов функции с передачей ссылки
        # threading.Thread(
        #     target=payment_with_timeout, args=(quickpay.redirected_url, 120.0)
        # ).start()
