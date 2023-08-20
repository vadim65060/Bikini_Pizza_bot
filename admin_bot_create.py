from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import constants
from classes import Config, CachedImages
from create_db import data_base

config = Config("config.json")
admins_bot = Bot(token=config.admin_bot_token)
storage = MemoryStorage()
admin_dp = Dispatcher(admins_bot, storage=storage)
store_cached_imgs = CachedImages(data_base, constants.STORE_PATH, constants.ADMIN_BOT_NAME)
