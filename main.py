from aiogram import executor, Dispatcher

import startup_functions
from bot_create import dp
from create_db import data_base
from database.db_funcs import DataBase
from handlers import registration_handlers, menu_handlers, store_handlers, order_handlers, order_escort_handlers, \
    order_redactor_handlers
from middleware import antispam, blacklist, admins


def users_bot_start(dp: Dispatcher, db: DataBase):
    print("users bot startup.")
    store_handlers.register_store_handlers()
    registration_handlers.register_registration_handlers()
    order_handlers.register_order_handlers()
    order_redactor_handlers.register_order_redactor_handlers()
    order_escort_handlers.register_order_escort_handlers()
    menu_handlers.register_menu_handlers()
    dp.middleware.setup(admins.AdminMalware(db))
    dp.middleware.setup(blacklist.BlacklistMiddleware(db))
    dp.middleware.setup(antispam.AntispamMiddleware())
    executor.start_polling(dp, on_startup=startup_functions.on_startup, on_shutdown=startup_functions.on_shutdown,
                           skip_updates=False)
    print("users bot is stopped.")


if __name__ == '__main__':
    users_bot_start(dp, data_base)
