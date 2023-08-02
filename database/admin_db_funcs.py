import sqlite3

from validator_collection import checkers

import constants
from database.db_funcs import DataBase
import datetime as dt


class AdminDataBase(DataBase):
    def __init__(self, path):
        super().__init__(path)

    def set_level_2_3_admin(self, tg_id, level, tg_who_gave):
        if self.execute("SELECT tg_id FROM admins WHERE tg_id = ?", tg_id, fetch="ONE"):
            self.execute("UPDATE admins SET level = ? WHERE tg_id = ?",
                         level, tg_id, commit=True)
        else:
            self.execute("""INSERT INTO admins(tg_id, level) VALUES (?, ?)""",
                         tg_id, level, commit=True)
        self.add_transaction(constants.TransactionTypes.ADMIN_GAVE.value,
                             tg_who_gave, tg_id, f"admin level {level} add")

    def add_promo(self, name, money, can_use, time_registered, time_ends, id_who_created):
        self.execute("INSERT INTO promo (name, money, can_use, time_registered, time_ends) VALUES (?, ?, ?, ?, ?)",
                     name, money, can_use, time_registered, time_ends, commit=True)
        self.add_transaction(constants.TransactionTypes.PROMO_CREATE.value,
                             id_who_created, None, f"{name}  money:{money}  can use:{can_use}")

    def get_promo_id(self, name):
        res = self.execute("SELECT id FROM promo WHERE name = ?", name, fetch="ONE")
        if not res or not res[0]:
            return False
        return res[0]

    def get_promo_list(self):
        res = self.execute("SELECT name, money, can_use, used, time_ends FROM promo", fetch=True)
        return list(map(lambda x:
                        [x[0],
                         x[1],
                         x[2],
                         x[3],
                         dt.datetime.strptime(x[4], constants.DATETIME_FORMAT).astimezone(constants.TZ)],
                        res))

    def issue_merch(self, purchase_id, k, checker_tg_id):
        # 0 - успех,  1 - нет такой записи, 2 - k < 0, 3 - k > count - issued, 4 - error
        any_records = self.execute("SELECT purchases.count, purchases.issued, purchases.tg_id, "
                                   "stuff.price, "
                                   "purchases.stuff_sizes_colors_id, purchases.stuff_id "
                                   "FROM purchases "
                                   "JOIN stuff ON purchases.stuff_id = stuff.id "
                                   "JOIN users ON purchases.tg_id = users.tg_id "
                                   "WHERE purchases.id = ?",
                                   purchase_id, fetch="ONE")
        if not any_records:
            return 1
        count, issued, tg_id, price, sizes_colors_id, stuff_id = any_records
        if k < 0:
            self.add_transaction(constants.TransactionTypes.ISSUE_MERCH_FAIL.value, checker_tg_id, tg_id,
                                 f"less than zero stuff_id: {stuff_id}, sizes_colors_id: {sizes_colors_id}")
            return 2
        if k > count - issued:
            self.add_transaction(constants.TransactionTypes.ISSUE_MERCH_FAIL.value, checker_tg_id, tg_id,
                                 f"too many to issue stuff_id: {stuff_id}, sizes_colors_id: {sizes_colors_id}")
            return 3
        fail = False
        cur = self.con.cursor()
        try:
            cur.execute("UPDATE purchases SET issued = issued + ? WHERE id = ?", (k, purchase_id))
            self.con.commit()
        except (sqlite3.DatabaseError, sqlite3.InternalError, sqlite3.OperationalError) as e:
            print(e)
            self.con.rollback()
            fail = True
        cur.close()
        if fail:
            self.add_transaction(constants.TransactionTypes.ISSUE_MERCH_FAIL.value, checker_tg_id, tg_id,
                                 f"updating error stuff_id: {stuff_id}, sizes_colors_id: {sizes_colors_id}")
            return 4
        else:

            self.add_transaction(constants.TransactionTypes.ISSUE_MERCH.value, checker_tg_id, tg_id,
                                 f"stuff_id: {stuff_id}, sizes_colors_id: {sizes_colors_id} returned: {k}")
            return 0

    def return_back_merch(self, purchase_id, k, checker_tg_id):
        any_records = self.execute("SELECT purchases.count, purchases.issued, purchases.tg_id, "
                                   "stuff.price, "
                                   "purchases.stuff_sizes_colors_id, purchases.stuff_id "
                                   "FROM purchases "
                                   "JOIN stuff ON purchases.stuff_id = stuff.id "
                                   "JOIN users ON purchases.tg_id = users.tg_id "
                                   "WHERE purchases.id = ?",
                                   purchase_id, fetch="ONE")
        if not any_records:
            return 1
        count, issued, tg_id, price, sizes_colors_id, stuff_id = any_records
        if k < 0:
            self.add_transaction(constants.TransactionTypes.MERCH_RETURN_BACK_FAIL.value, checker_tg_id, tg_id,
                                 f"less than zero stuff_id: {stuff_id}, sizes_colors_id: {sizes_colors_id}")
            return 2
        if k > count:
            self.add_transaction(constants.TransactionTypes.MERCH_RETURN_BACK_FAIL.value, checker_tg_id, tg_id,
                                 f"too many to return back stuff_id: {stuff_id}, sizes_colors_id: {sizes_colors_id}")
            return 3
        will_be_issued = min(issued, count - k)
        money_get = k * price

        fail = False
        cur = self.con.cursor()
        try:
            if count != k:
                cur.execute("UPDATE purchases SET count = count - ?, issued = ? WHERE id = ?", (k, will_be_issued,
                                                                                                purchase_id))
            else:
                cur.execute("DELETE FROM purchases WHERE id = ? ", (purchase_id,))
            cur.execute("UPDATE users SET money = money + ? WHERE tg_id = ?", (money_get, tg_id))
            if sizes_colors_id:
                cur.execute("UPDATE stuff_sizes_colors SET count = count + 1 WHERE id = ?", (sizes_colors_id,))
            else:
                cur.execute("UPDATE stuff SET count = count + 1 WHERE id = ?", (stuff_id,))
            self.con.commit()
        except (sqlite3.DatabaseError, sqlite3.InternalError, sqlite3.OperationalError) as e:
            print(e)
            self.con.rollback()
            fail = True
        cur.close()
        if fail:
            self.add_transaction(constants.TransactionTypes.MERCH_RETURN_BACK_FAIL.value, checker_tg_id, tg_id,
                                 f"updating error stuff_id: {stuff_id}, sizes_colors_id: {sizes_colors_id}")
            return 4
        else:
            self.add_transaction(constants.TransactionTypes.MERCH_RETURN_BACK.value, checker_tg_id, tg_id,
                                 f"stuff_id: {stuff_id}, sizes_colors_id: {sizes_colors_id} were given: {k}")
            return 0

    def add_stuff(self, user_id: int, category: str | int, name: str, description: str, price: int, img_path: str,
                  count: int):
        if not checkers.is_integer(category, minimum=1):
            category = self.execute("SELECT id FROM stuff_categories WHERE name = ?", category, fetch=True)

        self.execute(
            "INSERT INTO stuff(stuff_category_id, name, description, price, img_path, count) VALUES (?,?,?,?,?,?)",
            category, name, description, price, img_path, count, commit=True)
        self.add_transaction(constants.TransactionTypes.CREATE_STUFF.value,
                             user_id, None, f"user:{user_id}  add stuff {name}")

    def delete_stuff(self, user_id: int, stuff_id):
        self.execute("DELETE FROM stuff WHERE id = ?", stuff_id, commit=True)
        self.add_transaction(constants.TransactionTypes.DELETE_STUFF.value,
                             user_id, None, f"user:{user_id}  delete stuff {stuff_id}")

    def add_stuff_category(self, user_id: int, name: str, description: str, img_path: str):
        self.execute("INSERT INTO stuff_categories(name, description, img_path) VALUES (?,?,?)",
                     name, description, img_path, commit=True)
        self.add_transaction(constants.TransactionTypes.CREATE_STUFF_CATEGORY.value,
                             user_id, None, f"user:{user_id}  add stuff category {name}")

    def delete_category(self, user_id: int, category_id):
        self.execute("DELETE FROM stuff_categories WHERE id = ?", category_id, commit=True)
        self.add_transaction(constants.TransactionTypes.DELETE_STUFF_CATEGORY.value,
                             user_id, None, f"user:{user_id}  delete category {category_id}")

    def __update_table_value(self, user_id: int, table: str, what: str, column_name: str, item: str | int,
                             value: int | str, transaction_type: constants.TransactionTypes):
        self.execute(f"UPDATE {table} SET {what} = ? WHERE {column_name} = ?", value, item, fetch="one")
        self.add_transaction(transaction_type.value, user_id, None,
                             f"user:{user_id}  update {table} {what} to {value}")

    def update_stuff(self, user_id: int, what: str, stuff_id: str, value: int | str):
        self.__update_table_value(user_id, 'stuff', what, 'id', stuff_id, value,
                                  constants.TransactionTypes.UPDATE_STUFF)

    def update_stuff_category(self, user_id: int, what: str, category_id: int, value: str):
        self.__update_table_value(user_id, 'stuff_categories', what, 'id', category_id, value,
                                  constants.TransactionTypes.UPDATE_STUFF_CATEGORY)

    def delete_cache_img(self, img_path: str):
        self.execute("DELETE FROM img_cache WHERE path = ?", img_path, commit=True)


if __name__ == '__main__':
    db = AdminDataBase("mmweek2023db.db")
