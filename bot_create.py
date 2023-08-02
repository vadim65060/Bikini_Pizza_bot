from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import classes
import constants
from classes import Config
from create_db import data_base

config = Config("config.json")
users_bot = Bot(token=config.bot_token)
storage = MemoryStorage()
dp = Dispatcher(users_bot, storage=storage)
store_cached_imgs = classes.CachedImages(data_base, constants.STORE_PATH, constants.USER_BOT_NAME)
