import datetime as dt
import sqlite3
from typing import Union

import constants


class DataBase:
    def __init__(self, path):
        self.con = sqlite3.connect(path)
        self.create()

    def create(self):
        self.execute("""CREATE TABLE IF NOT EXISTS users(
                        tg_id INTEGER NOT NULL PRIMARY KEY,
                        username TEXT,
                        money   INTEGER NOT NULL DEFAULT 0);""",
                     commit=True)

        self.execute("""CREATE TABLE IF NOT EXISTS blacklist(
                                    tg_id INTEGER NOT NULL PRIMARY KEY);""",
                     commit=True)

        self.execute("""CREATE TABLE IF NOT EXISTS admins (
                            id       INTEGER PRIMARY KEY AUTOINCREMENT
                                             NOT NULL,
                            tg_id    INTEGER NOT NULL,
                            level    INTEGER
                        );
                        """,
                     commit=True)

        self.execute("""CREATE TABLE IF NOT EXISTS stuff (
                                id                INTEGER PRIMARY KEY AUTOINCREMENT,
                                stuff_category_id INTEGER REFERENCES stuff_categories (id),
                                name              TEXT,
                                description       TEXT,
                                price             INTEGER,
                                img_path          TEXT,
                                count             INTEGER,
                                show              INTEGER DEFAULT (1) 
                            );""",
                     commit=True)

        self.execute("""CREATE TABLE IF NOT EXISTS stuff_categories (
                                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                                    name        TEXT,
                                    description TEXT,
                                    img_path    TEXT
                                );
                                """, commit=True)

        self.execute("""CREATE TABLE IF NOT EXISTS purchases (
                            id                    INTEGER PRIMARY KEY AUTOINCREMENT,
                            tg_id                 INTEGER NOT NULL
                                                          REFERENCES users (tg_id),
                            stuff_id              INTEGER REFERENCES stuff (id),
                            stuff_sizes_id        INTEGER REFERENCES stuff_sizes (id),
                            count                 INTEGER NOT NULL,
                            UNIQUE (
                                tg_id,
                                stuff_id,
                                stuff_sizes_id
                            )
                            
                        );""", commit=True)

        self.execute("""CREATE TABLE IF NOT EXISTS texts(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE,
                        content TEXT);
                        """, commit=True)

        self.execute("""CREATE TABLE IF NOT EXISTS promo(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL,
                        money INTEGER NOT NULL,
                        can_use INTEGER NOT NULL,
                        used INTEGER NOT NULL DEFAULT 0,
                        time_registered TEXT NOT NULL,
                        time_ends TEXT NOT NULL);""",
                     commit=True)

        self.execute("""CREATE TABLE IF NOT EXISTS promo_usages(
                                promo_id TEXT NOT NULL,
                                tg_id INTEGER NOT NULL,
                                datetime TEXT NOT NULL,
                                CONSTRAINT was PRIMARY KEY (promo_id, tg_id));""",
                     commit=True)

        self.execute("""CREATE TABLE IF NOT EXISTS transactions(
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                type TEXT NOT NULL,
                                tg_id1 INTEGER,
                                tg_id2 INTEGER,
                                datetime TEXT,
                                data TEXT);
                                """, commit=True)
        self.execute("""CREATE TABLE IF NOT EXISTS stuff_sizes (
                            id       INTEGER PRIMARY KEY AUTOINCREMENT,
                            stuff_id INTEGER REFERENCES stuff (id),
                            size     TEXT,
                            price    INTEGER NOT NULL,
                            count    INTEGER NOT NULL
                        );
                        """, commit=True)
        self.execute("""CREATE TABLE IF NOT EXISTS img_cache (
                        id     INTEGER PRIMARY KEY AUTOINCREMENT,
                        path   TEXT,
                        bot_name TEXT,
                        img_id TEXT
                    )""", commit=True)
        self.execute("""CREATE TABLE IF NOT EXISTS shops (
                                id     INTEGER PRIMARY KEY AUTOINCREMENT,
                                address   TEXT NOT NULL,
                                show      INTEGER DEFAULT 1
                            )""", commit=True)
        self.execute("""CREATE TABLE IF NOT EXISTS orders (
                                        id     INTEGER PRIMARY KEY AUTOINCREMENT,
                                        user_id       INTEGER,
                                        stuff_ids     TEXT,
                                        price         INTEGER,
                                        used_balls    INTEGER,
                                        delivery_cost INTEGER,
                                        phone         TEXT,
                                        address       TEXT,
                                        comment       TEXT
                                    )""", commit=True)

    def execute(self, clause: str, *args, commit: bool = False, fetch: Union[bool, str] = False) -> Union[list, None]:
        """
        Запрос к БД SQLite
        :param clause:
        :param args: Аргументы, замещающие "?" в запросе
        :param commit:
        :param fetch: Сколько данных нужно возвращать: True | "ALL" - все, "ONE" - одну запись, False - ничего
        :return:
        """
        cur = self.con.cursor()
        executor = cur.execute(clause, args)
        if commit:
            self.con.commit()

        data = None

        if fetch:
            if isinstance(fetch, str) and fetch.upper() == "ALL" or isinstance(fetch, bool) and fetch:
                data = executor.fetchall()
            elif isinstance(fetch, str) and fetch.upper() == "ONE":
                data = executor.fetchone()
            else:
                raise ValueError("Неверный fetch аргумент.")

        cur.close()

        if fetch:
            return data

    def in_blacklist(self, tg_id):
        data = self.execute("SELECT tg_id FROM blacklist WHERE tg_id = ?", tg_id, fetch="one")
        if not data:
            return False
        return True

    def is_size_stuff(self, stuff_id):
        data = self.execute("SELECT count FROM stuff WHERE id = ?", stuff_id, fetch="one")
        if not data:
            raise ValueError("Bad stuff id.")
        if data[0] is None:
            return True
        return False

    def get_purchases_num_by_stuff_id(self, stuff_id):  # Для вещей без укзания размера/цвета
        data = self.execute("SELECT count FROM purchases WHERE stuff_id = ?", stuff_id, fetch=True)
        res = 0
        for count, in data:
            res += count
        return res

    def get_category_id_by_name(self, category_name):
        data = self.execute("SELECT id FROM stuff_categories WHERE name = ?", category_name, fetch="one")
        if not data or not data[0]:
            return None
        return data[0]

    def get_category_img_path(self, category_id):
        data = self.execute("SELECT img_path FROM stuff_categories WHERE id = ?", category_id, fetch="one")
        if not data or not data[0]:
            return None
        return data[0]

    def get_category_description(self, category_id):
        data = self.execute("SELECT description FROM stuff_categories WHERE id = ?", category_id, fetch="one")
        if not data or not data[0]:
            return ""
        return data[0]

    def get_stuff_img_path(self, stuff_id):
        data = self.execute("SELECT img_path FROM stuff WHERE id = ?", stuff_id, fetch="one")
        if not data or not data[0]:
            return None
        return data[0]

    def how_many_stuff_booked(self, tg_id, stuff_id):
        data = self.execute("SELECT count FROM purchases WHERE tg_id = ? and stuff_id = ?",
                            tg_id, stuff_id, fetch="ALL")
        res = 0
        for count, in data:
            res += count
        return res

    def how_many_sizes_booked(self, tg_id, stuff_sizes_id):
        data = self.execute("SELECT count FROM purchases WHERE tg_id = ? and stuff_sizes_id = ?",
                            tg_id, stuff_sizes_id, fetch="ALL")
        res = 0
        for count, in data:
            res += count
        return res

    def get_staff_list_info(self, staff_list: list):
        """
        :param staff_list: [(stuff_id, stuff_sizes_id, count)]
        :return: [(stuff_id, stuff_sizes_id, name, price, size, count)]
        """
        res = []
        for stuff_id, stuff_sizes_id, count in staff_list:
            name, = self.get_stuff_info(stuff_id, "name")
            if stuff_sizes_id is not None:
                price, size = self.get_stuff_sizes_texts_info(stuff_sizes_id, "price, size")
            else:
                price, = self.get_stuff_info(stuff_id, "price")
                size = None
            res.append((stuff_id, stuff_sizes_id, name, price, size, count))
        return res

    def booked_list(self, tg_id: int):
        """
        :param tg_id:
        :return: [(stuff_id, stuff_sizes_id, name, price, size, count)]
        """
        data = self.execute("SELECT stuff_id, stuff_sizes_id, count "
                            "FROM purchases WHERE tg_id = ?",
                            tg_id, fetch="ALL")
        return self.get_staff_list_info(data)

    def get_order_list(self, order_id):
        """
        :param order_id:
        :return: [(stuff_id, stuff_sizes_id, name, price, size, count)]
        """
        return self.get_staff_list_info(self.parse_order_purchases(order_id))

    def get_stuff_count_num_by_stuff_id(self, stuff_id):
        """
        Подсчитывает количество на складе любой вещи
        :param stuff_id:
        :return:
        """
        data = self.execute("SELECT count FROM stuff WHERE id = ?", stuff_id, fetch="one")
        if not data:
            return None
        if data[0] is not None:
            return data[0]
        data = self.execute("SELECT count FROM stuff_sizes WHERE stuff_id = ?", stuff_id, fetch=True)
        res = 0
        for count, in data:
            res += count
        return res

    def get_purchases_num_by_sizes_id(self, stuff_sizes_id):  # Для определённого цвета/размера вещи
        data = self.execute("SELECT count FROM purchases WHERE stuff_sizes_id = ?", stuff_sizes_id,
                            fetch=True)
        res = 0
        for count, in data:
            res += count
        return res

    def get_all_size_combinations(self, stuff_id):
        """
        Возвращает [(size_id, price, size, count),...]
        :param stuff_id:
        :return:
        """
        stuff = self.execute(
            "SELECT id, price, size, count FROM stuff_sizes WHERE stuff_id = ?",
            stuff_id,
            fetch=True)
        res = []
        for size_id, price, size, count in stuff:
            if count > 0:
                res.append((size_id, price, size, count))
        return res

    # def get_all_colors_by_stuff_id(self, stuff_id):
    #     """
    #     Возвращает [(colors_sizes_id, color) for colors_sizes_id, color in ...]
    #     :param stuff_id:
    #     :return:
    #     """
    #     res = []
    #     colors = self.execute(
    #         "SELECT id, color, count FROM stuff_sizes_colors WHERE stuff_id = ? and color IS NOT NULL",
    #         stuff_id,
    #         fetch=True)
    #     for colors_sizes_id, color, count in colors:
    #         if count > 0:
    #             res.append((colors_sizes_id, color))
    #     return res

    def get_all_sizes_by_stuff_id(self, stuff_id):
        """
        Возвращает [(sizes_id, size) for sizes_id, size in ...]
        :param stuff_id:
        :return:
        """
        res = []
        sizes = self.execute(
            "SELECT id, size, count FROM stuff_sizes WHERE stuff_id = ? and size IS NOT NULL",
            stuff_id,
            fetch=True)
        for sizes_id, size, count in sizes:
            if count > 0:
                res.append((sizes_id, size))
        return res

    def get_stuff_sizes(self, sizes_id, what: str):
        data = self.execute("SELECT " + what + " FROM stuff_sizes WHERE id = ?", sizes_id,
                            fetch="one")
        return data

    def get_stuff_categories(self):
        data = self.execute("SELECT id, name FROM stuff_categories", fetch=True)
        return data

    def get_stuff_category_id(self, category_name):
        return self.execute("SELECT id FROM stuff_categories WHERE name = ?", category_name, fetch='one')

    def get_user_money(self, tg_id):
        data = self.get_user_info(tg_id, "money")
        if not data:
            return None
        return data[0]

    def get_stuff_sizes_texts_info(self, sizes_id, what: str):
        data = self.execute("SELECT " + what + " FROM stuff_sizes WHERE id = ?",
                            sizes_id, fetch="one")
        return data

    def get_stuff_category_info(self, stuff_category_id, what: str):
        return self.execute("SELECT " + what + " FROM stuff_categories WHERE id = ?", stuff_category_id, fetch="one")

    def get_stuff_info(self, stuff_id, what: str):
        return self.execute("SELECT " + what + " FROM stuff WHERE id = ?", stuff_id, fetch="one")

    def get_stuff_info_by_id_array(self, stuff_id_array: list[int], what: str):
        ttt = f"SELECT {what} FROM stuff WHERE id IN {stuff_id_array}".replace('[', '(').replace(']', ')')
        return self.execute(ttt, fetch=True)

    def get_stuff_info_by_name(self, stuff_name: str, what: str):
        return self.execute("SELECT " + what + " FROM stuff WHERE name = ?", stuff_name, fetch="one")

    def delete_user_purchase(self, tg_id: int, staff_id: int, size_id: int | None = None, count: int | None = None):
        select_size = ''
        if size_id is not None:
            select_size = f' AND stuff_sizes_id = {size_id}'
        if count is None:
            self.execute("DELETE FROM purchases WHERE tg_id = ? AND stuff_id = ?{}".format(select_size), tg_id,
                         staff_id, commit=True)
            return

        staff_count = self.execute("SELECT count FROM purchases WHERE tg_id = ? AND stuff_id = ?{}".format(select_size),
                                   tg_id, staff_id,
                                   fetch='ONE')
        if staff_count is None:
            return

        staff_count, = staff_count
        if staff_count > count:
            self.execute(
                "UPDATE purchases SET count = count - ? WHERE tg_id = ? AND stuff_id = ?{}".format(select_size), count,
                tg_id,
                staff_id, commit=True)
        else:
            self.execute("DELETE FROM purchases WHERE tg_id = ? AND stuff_id = ?{}".format(select_size), tg_id,
                         staff_id, commit=True)

    def add_user_purchase(self, tg_id: int, staff_id: int, size_id: int | None = None, count: int | None = None):
        select_size = ''
        if size_id is not None:
            select_size = f' AND stuff_sizes_id = {size_id}'
        staff_count = self.execute(
            "SELECT count FROM purchases WHERE tg_id = ? AND stuff_id = ?{}".format(select_size),
            tg_id, staff_id, fetch='ONE')
        if staff_count is None:
            self.execute(f'INSERT INTO purchases (tg_id, stuff_id, stuff_sizes_id, count) VALUES (?, ?, ?, ?)', tg_id,
                         staff_id, size_id, count, fetch=True)
        else:
            self.execute(
                'UPDATE purchases SET count = count + ? WHERE tg_id = ? AND stuff_id = ?{}'.format(select_size),
                count, tg_id, staff_id, fetch=True)

    # def get_user_info_by_code(self, code: str, what: str):
    #     return self.execute("SELECT " + what + " FROM users WHERE enter_code = ?", code, fetch="one")

    def get_stuff_by_category_id(self, stuff_category_id: int, what: str):
        data = self.execute("SELECT " + what + " FROM stuff WHERE stuff_category_id = ?", stuff_category_id, fetch=True)
        return data

    def have_admin_rights(self, tg_id, level):
        data = self.execute("SELECT level FROM admins WHERE tg_id = ?", tg_id, fetch="ONE")
        if data and data[0] >= level:
            return True
        return False

    def add_user(self, tg_id, username):
        self.add_transaction(constants.TransactionTypes.USER_REGISTER.value,
                             tg_id,
                             None, None)
        self.execute("INSERT INTO users (tg_id, username) VALUES (?, ?) "
                     "ON CONFLICT(tg_id) DO UPDATE SET username = ?",
                     tg_id, username, username,
                     commit=True)

    def add_money(self, tg_id, money, transaction_data=None):
        self.add_transaction(constants.TransactionTypes.MONEY_GET.value,
                             tg_id,
                             None,
                             transaction_data)
        self.execute("UPDATE users SET money = money + ? WHERE tg_id = ?", money, tg_id, commit=True)

    def get_text(self, name):
        res = self.execute("SELECT content FROM texts WHERE name = ?", name, fetch="ONE")
        if not res or not res[0]:
            return False
        return res[0]

    def get_help_text(self):
        return self.get_text("help")

    def get_user_info(self, tg_id, what: str):
        """
        Вытаскивает заданные в what колонки определённого пользователя
        :param tg_id:
        :param what:
        :return:
        """
        return self.execute("SELECT " + what + " FROM users WHERE tg_id = ?", tg_id, fetch="ONE")

    def get_user_id_by_username(self, username):
        if username.startswith("@"):
            username = username[1:]
        tg_id = self.execute("SELECT tg_id FROM users WHERE username LIKE ?", username, fetch="ONE")
        if not tg_id:
            return None
        return tg_id[0]

    def user_registered(self, tg_id):
        return bool(self.get_user_info(tg_id, "tg_id"))

    def use_promo(self, tg_id, promo):
        """

        :param tg_id:
        :param promo:
        :return: 0 - сработало, 1 - нет кода, 2 - уже использовано, 3 - просрочен, 4 - использован много раз,
         5 - транзакция не завершена
        """
        data = self.execute("SELECT id, money, time_ends, used, can_use FROM promo WHERE name = ?",
                            promo,
                            fetch="one")
        if not data:
            self.add_transaction(constants.TransactionTypes.PROMO_USAGE.value,
                                 tg_id,
                                 None,
                                 f"promo: {promo} doesn't activated: doesn't exists")
            return 1
        promo_id, money, time_ends, used, can_use = data
        if promo_id:
            dt_ends = dt.datetime.strptime(time_ends, constants.DATETIME_FORMAT).astimezone(constants.TZ)
            if dt.datetime.now(constants.TZ) <= dt_ends:
                if used < can_use or can_use == -1:
                    used_user = self.execute("SELECT promo_id FROM promo_usages WHERE promo_id = ? and tg_id = ?",
                                             promo_id,
                                             tg_id, fetch="one")
                    if not used_user:
                        cur = self.con.cursor()
                        fail = False
                        try:
                            cur.execute("INSERT INTO promo_usages (promo_id, tg_id, datetime) VALUES (?, ?, ?);",
                                        (promo_id, tg_id,
                                         dt.datetime.strftime(dt.datetime.now(tz=constants.TZ),
                                                              constants.DATETIME_FORMAT)))
                            cur.execute("UPDATE promo SET used = used + 1 WHERE id = ?;", (promo_id,)),
                            cur.execute("UPDATE users SET money = money + ? WHERE tg_id = ?;", (money, tg_id))
                        except (sqlite3.DatabaseError, sqlite3.InternalError) as e:
                            fail = True
                            self.con.rollback()
                        cur.close()
                        if fail:
                            self.add_transaction(constants.TransactionTypes.PROMO_USAGE.value,
                                                 tg_id,
                                                 None,
                                                 f"promo: {promo} doesn't activated bad transaction")
                            return 5
                        else:
                            self.add_transaction(constants.TransactionTypes.PROMO_USAGE.value,
                                                 tg_id,
                                                 None,
                                                 f"promo: {promo} activated {money} added")
                            return 0
                    else:
                        self.add_transaction(constants.TransactionTypes.PROMO_USAGE.value,
                                             tg_id,
                                             None,
                                             f"promo: {promo} doesn't activated: already used")
                        return 2
                else:
                    self.add_transaction(constants.TransactionTypes.PROMO_USAGE.value,
                                         tg_id,
                                         None,
                                         f"promo: {promo} doesn't activated: used too many times")
                    return 4
            else:
                self.add_transaction(constants.TransactionTypes.PROMO_USAGE.value,
                                     tg_id,
                                     None,
                                     f"promo: {promo} doesn't activated: expired")
                return 3
        else:
            self.add_transaction(constants.TransactionTypes.PROMO_USAGE.value,
                                 tg_id,
                                 None,
                                 f"promo: {promo} doesn't activated: doesn't exists")
            return 1

    def add_transaction(self, transaction_type, tg_id1, tg_id2, data):
        """

        :param transaction_type:
        :param tg_id1:
        :param tg_id2:
        :param data:
        :return:
        """
        datetime = dt.datetime.now(tz=constants.TZ).strftime(constants.LOG_DATETIME_FORMAT)
        self.execute("INSERT INTO transactions (type, tg_id1, tg_id2, datetime, data) VALUES (?, ?, ?, ?, ?)",
                     transaction_type, tg_id1, tg_id2, datetime, data, commit=True)

    def get_last_transaction(self, transaction_type, tg_id1=None, tg_id2=None):
        if tg_id2 is None:
            data = self.execute("SELECT type, tg_id1, tg_id2, datetime, data FROM transactions "
                                "WHERE type = ? and tg_id1 = ?",
                                transaction_type, tg_id1, fetch="all")
        elif tg_id1 is None:
            data = self.execute("SELECT type, tg_id1, tg_id2, datetime, data FROM transactions "
                                "WHERE type = ? and tg_id2 = ?",
                                transaction_type, tg_id2, fetch="all")
        else:
            data = self.execute("SELECT type, tg_id1, tg_id2, datetime, data FROM transactions "
                                "WHERE type = ? and tg_id1 = ? and tg_id2 = ?",
                                transaction_type, tg_id1, tg_id2, fetch="all")
        if not data:
            return None
        maxim = max(data, key=lambda x:
        dt.datetime.strptime(x[3], constants.LOG_DATETIME_FORMAT).astimezone(tz=constants.TZ))

        return dt.datetime.strptime(maxim[3], constants.LOG_DATETIME_FORMAT).astimezone(tz=constants.TZ)

    def get_last_support_request_time(self, tg_id):
        data = self.get_last_transaction(constants.TransactionTypes.SUPPORT_REQUEST.value, tg_id1=tg_id)
        if not data:
            return None
        return data

    def get_admin_list(self, level=None):
        if level is not None:
            data = self.execute("SELECT tg_id FROM admins WHERE level = ?", level, fetch=True)
        else:
            data = self.execute("SELECT tg_id FROM admins", fetch=True)
        res = []
        for tg_id in data:
            username, = self.get_user_info(tg_id[0], "username")
            res.append((tg_id[0], username))
        return res

    # 1 - недостаточно денег, 2 - мерча уже нет, 3 - ошибка при транзакции
    def buy_size_stuff(self, tg_id, sizes_id):
        stuff_id, count = self.get_stuff_sizes_texts_info(sizes_id, "stuff_id, count")
        price, = self.get_stuff_info(stuff_id, "price")
        user_money = self.get_user_money(tg_id)
        if user_money < price:
            self.add_transaction(constants.TransactionTypes.PURCHASE_FAIL.value, tg_id, None,
                                 f"not enough money, sizes_id = {sizes_id}")
            return 1
        elif count <= 0:
            self.add_transaction(constants.TransactionTypes.PURCHASE_FAIL.value, tg_id, None,
                                 f"not enough items, sizes_id = {sizes_id}")
            return 2
        else:
            cur = self.con.cursor()
            fail = False
            try:
                cur.execute("UPDATE users SET money = money - ? WHERE tg_id = ?;", (price, tg_id))
                cur.execute("UPDATE stuff_sizes SET count = count - 1 WHERE id = ?;", (sizes_id,))
                cur.execute("INSERT INTO purchases (tg_id, stuff_id, stuff_sizes_id, count) "
                            "VALUES (?, ?, ?, 1) "
                            "ON CONFLICT (tg_id, stuff_id, stuff_sizes_id) DO UPDATE SET count = count + 1 "
                            "WHERE tg_id = ? and stuff_id = ? and stuff_sizes_id = ?",
                            (tg_id, stuff_id, sizes_id, tg_id, stuff_id, sizes_id))
                # update purchases
                self.con.commit()
            except (sqlite3.DatabaseError, sqlite3.InternalError) as e:
                print(e)
                self.con.rollback()
                fail = True
            cur.close()
            if fail:
                self.add_transaction(constants.TransactionTypes.PURCHASE_FAIL.value, tg_id, None,
                                     f"transaction fail, sizes_id = {sizes_id}")
                return 3
            self.add_transaction(constants.TransactionTypes.PURCHASE_SUCCESS.value, tg_id, None,
                                 f"sizes_id = {sizes_id}")
            return 0

    # 1 - недостаточно денег, 2 - мерча уже нет, 3 - ошибка при транзакции
    def buy_no_size_stuff(self, tg_id, stuff_id):
        price, count = self.get_stuff_info(stuff_id, "price, count")
        # user_money = self.get_user_money(tg_id)
        if self.execute("SELECT id FROM purchases WHERE tg_id = ? and stuff_id = ?",
                        tg_id, stuff_id, fetch="one"):
            have_purchase = True
        else:
            have_purchase = False
        # if user_money < price:
        #     self.add_transaction(constants.TransactionTypes.PURCHASE_FAIL.value, tg_id, None,
        #                          f"not enough money, stuff_id = {stuff_id}")
        #     return 1
        if count <= 0:
            self.add_transaction(constants.TransactionTypes.PURCHASE_FAIL.value, tg_id, None,
                                 f"not enough items, stuff_id = {stuff_id}")
            return 2
        else:
            cur = self.con.cursor()
            fail = False
            try:
                # cur.execute("UPDATE users SET money = money - ? WHERE tg_id = ?;", (price, tg_id))
                cur.execute("UPDATE stuff SET count = count - 1 WHERE id = ?;", (stuff_id,))
                if not have_purchase:
                    cur.execute("INSERT INTO purchases (tg_id, stuff_id, stuff_sizes_id, count) "
                                "VALUES (?, ?, NULL, 1) ",
                                (tg_id, stuff_id))
                else:
                    cur.execute("UPDATE purchases SET count = count + 1 "
                                "WHERE tg_id = ? and stuff_id = ? and stuff_sizes_id is NULL",
                                (tg_id, stuff_id))
                self.con.commit()
            except (sqlite3.DatabaseError, sqlite3.InternalError) as e:
                print(e)
                fail = True
                self.con.rollback()
            cur.close()
            if fail:
                self.add_transaction(constants.TransactionTypes.PURCHASE_FAIL.value, tg_id, None,
                                     f"transaction fail, stuff_id = {stuff_id}")
                return 3
            self.add_transaction(constants.TransactionTypes.PURCHASE_SUCCESS.value, tg_id, None,
                                 f"stuff_id = {stuff_id}")
            return 0

    def get_order_sum(self, tg_id: int):
        booked_list = self.booked_list(tg_id)
        order_sum = 0
        for i in range(len(booked_list)):
            order_sum += booked_list[i][3] * booked_list[i][5]
        return order_sum

    def get_purchases_by_id(self, tg_id: int, what: str):
        return self.execute(f"SELECT {what} FROM purchases WHERE tg_id = ?", tg_id, fetch=True)

    def get_shops(self):
        return self.execute("SELECT id, address FROM shops WHERE show = 1", fetch=True)

    def is_shop(self, address: str):
        return self.execute("SELECT id FROM shops WHERE address = ?", address, fetch='ONE')

    def get_shop_address(self, shop_id: int):
        return self.execute("SELECT address FROM shops WHERE id = ? AND show = 1", shop_id, fetch='ONE')

    def checkout(self, user_id: int, price: int, balls: int, delivery_cost: int, phone: str, address: str,
                 comment: str):
        purchases_text = self.__purchases_to_text(user_id)
        self.execute(
            "INSERT INTO orders (user_id, stuff_ids, price, used_balls, delivery_cost, phone, address, comment) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            user_id, purchases_text, price, balls, delivery_cost, phone, address, comment)
        self.execute("DELETE FROM purchases WHERE tg_id = ?", user_id)
        if balls is None:
            balls = 0
        self.execute("UPDATE users SET money = money - ? + ? WHERE tg_id = ?", balls,
                     int(price * constants.CASHBACK_PERCENT), user_id, commit=True)
        return self.execute('SELECT MAX(id) FROM orders WHERE user_id = ?', user_id, fetch='ONE')

    def get_last_user_order(self, user_id: int, what: str):
        order = self.execute(f"SELECT {what} FROM orders WHERE user_id = ?", user_id, fetch=True)
        if not order:
            return None
        return order[-1]

    def get_order_info(self, oder_id: int, what: str):
        return self.execute(f"SELECT {what} FROM orders WHERE id = ?", oder_id, fetch='ONE')

    def __purchases_to_text(self, user_id: int):
        purchases = self.get_purchases_by_id(user_id, 'stuff_id, stuff_sizes_id, count')
        purchases_text = ''
        for pur in purchases:
            purchases_text += f"{pur[0]}:{pur[1]}={pur[2]}, "
        return purchases_text[:-2]

    def parse_order_purchases(self, order_id: int):
        """

        :param order_id:
        :return: [(stuff_id, size_id, count)]
        """
        purchases_text: list[str] = \
            self.execute(f'SELECT stuff_ids FROM orders WHERE id = ?', order_id, fetch='ONE')[0].split(',')
        purchases = []
        for purchase in purchases_text:
            if purchase == ' ':
                continue

            stuff_and_size_id, count = purchase.split('=')
            stuff_id, size_id = stuff_and_size_id.split(':')
            size_id = int(size_id) if size_id != 'None' else None
            purchases.append((int(stuff_id), size_id, int(count)))
        return purchases

    def __del__(self):
        self.con.close()


if __name__ == '__main__':
    db = DataBase("mmweek2023db.db")
