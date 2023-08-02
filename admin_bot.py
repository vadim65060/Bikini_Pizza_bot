from aiogram import executor, Dispatcher

import startup_functions
from database.admin_db_funcs import AdminDataBase
from middleware import admins, blacklist

from create_db import data_base
from admin_bot_create import admin_dp
from handlers import admin_menu_handlers


def admin_bot_start(dp: Dispatcher, db: AdminDataBase):
    print("Bot startup.")
    admin_menu_handlers.register_admin_menu_handlers()
    dp.middleware.setup(admins.AdminMalware(db))
    dp.middleware.setup(blacklist.BlacklistMiddleware(db))
    executor.start_polling(dp, on_startup=startup_functions.on_startup, on_shutdown=startup_functions.on_shutdown)
    print("Bot is stopped.")


if __name__ == '__main__':
    admin_bot_start(admin_dp, data_base)
