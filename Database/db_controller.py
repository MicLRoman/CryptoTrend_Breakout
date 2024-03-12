import sqlite3
from os import path
from time import sleep


def infinite_retry(func):
    def wrapper(*args, **kwargs):
        while True:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"Exception caught: {e}, retrying...")
                sleep(1)

    return wrapper


class Controller:
    """Controls all operations with sqlite database"""

    def __init__(self, db_name: str = "DB") -> None:
        """Creates db if it doesn't exist, connects to db
        Args:
            db_name (str, optional) Defaults to "MessageEvents".
        """
        self.sqlite_name = db_name
        if not path.exists(f"Database/{db_name}.sqlite"):
            self._create_db()
        self.conn = sqlite3.connect(
            f"Database/{db_name}.sqlite", check_same_thread=False
        )
        self.cursor = self.conn.cursor()

    def _create_db(self) -> None:
        """Private method, used to create and init db"""
        conn = sqlite3.connect(
            f"Database/{self.sqlite_name}.sqlite", check_same_thread=False
        )
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE UserSubscriptions (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                ChatID INTEGER,
                Subscription INTEGER,
                DateOfEnd TEXT,
                SenderUsername TEXT,
                Discount INTEGER
            )
        """
        )

        conn.commit()
        cursor.close()
        conn.close()

    def add_user_with_sub(
        self,
        chat_id: int,
        subscription: bool,
        date_of_end: str,
        sender_username: str,
        discount: int
    ) -> None:
        sql = """
            INSERT INTO UserSubscriptions (
                ChatID,
                Subscription,
                DateOfEnd,
                SenderUsername,
                Discount
            ) VALUES (?, ?, ?, ?, ?)
        """

        self.cursor.execute(
            sql,
            (
                chat_id,
                subscription,
                date_of_end,
                sender_username,
                discount
            ),
        )

        self.conn.commit()


    def update_dateofend_of_subscription_of_user_with_sub(self, chat_id, data) -> None:
        """Update days of subscription of user by chat_id"""

        query = "UPDATE UserSubscriptions SET DateOfEnd = ? WHERE ChatID = ?"
        self.cursor.execute(query, (data, chat_id))

        self.conn.commit()

    def update_subscription_of_user_with_sub(self, chat_id, data) -> None:
        """Update days of subscription of user by chat_id"""

        query = "UPDATE UserSubscriptions SET Subscription = ? WHERE ChatID = ?"
        self.cursor.execute(query, (data, chat_id))

        self.conn.commit()

    def update_dateofend_of_subscription_of_user_with_sub(self, chat_id, data) -> None:
        """Update days of subscription of user by chat_id"""

        query = "UPDATE UserSubscriptions SET DateOfEnd = ? WHERE ChatID = ?"
        self.cursor.execute(query, (data, chat_id))

        self.conn.commit()

    def check_the_existing_of_user(self, chat_id) -> bool:
        """Check the existing of user in db by chat_id"""
        # Проверка наличия строки с определенным id

        query = "SELECT * FROM UserSubscriptions WHERE ChatID = ?"

        self.cursor.execute(query, (chat_id,))

        # Получение результатов
        row = self.cursor.fetchone()

        if row is None:
            return False
        else:
            return True

    def delete_the_existing_of_user(self, chat_id) -> None:
        """delete data of user by chat_id"""

        query = "DELETE FROM UserSubscriptions WHERE ChatID = ?"
        self.cursor.execute(query, (chat_id,))

        self.conn.commit()

    def delete_the_existing_of_user_with_sub_by_date(self, date_of_start) -> None:
        """delete data of user by chat_id"""

        query = "DELETE FROM UserSubscriptions WHERE DateOfEnd = ?"
        self.cursor.execute(query, (date_of_start,))

        self.conn.commit()

    def get_users_with_sub(self, subscription: int):
        """aa"""
        query = "SELECT ChatID FROM UserSubscriptions WHERE Subscription=?"
        self.cursor.execute(query, (subscription,))
        result = self.cursor.fetchall()

        return result


    # def get_user_with_sub_by_username(self, user_username: int) -> dict:
    #     """Returns dict with data about user where each key is a column name"""
    #     query = "SELECT * FROM UserSubscriptions WHERE SenderUsername = ? ORDER BY DateOfStart ASC LIMIT 1"
    #     self.cursor.execute(query, (user_username,))
    #     result = self.cursor.fetchone()

    #     if result is None:
    #         return {}  # User not found

    #     # Convert the row into a dictionary
    #     columns = [description[0] for description in self.cursor.description]
    #     users_dict = {}
    #     for i, column in enumerate(columns):
    #         users_dict[column] = result[i]

    #     return users_dict

    def get_user_with_sub_by_chat_id(self, chat_id: int) -> dict:
        """Returns dict with data about user where each key is a column name"""
        query = "SELECT * FROM UserSubscriptions WHERE ChatID = ? ORDER BY DateOfEnd ASC LIMIT 1"
        self.cursor.execute(query, (chat_id,))
        result = self.cursor.fetchone()

        if result is None:
            return {}  # User not found

        # Convert the row into a dictionary
        columns = [description[0] for description in self.cursor.description]
        users_dict = {}
        for i, column in enumerate(columns):
            users_dict[column] = result[i]

        return users_dict

    def get_all_user_ids(self):
        query = "SELECT ChatID FROM UserSubscriptions"
        res = self.cursor.execute(query)

        chatids = []
        for row in res:
            chatids.append(row[0])

        return chatids
        