import json
import os

from aiogram.types import ParseMode, Message, InlineKeyboardMarkup, InputFile, InputMediaPhoto

from database.db_funcs import DataBase

CONFIG_TEMPLATE = """{
  "tg_bot_token": "",
  "provider_token": "",
  "db_path": "database/mmweek2023db.db",
  "orders_chat_id": "",
  "support_chat_id": "",
  "org_bot_token": ""
}
"""


class Config:
    def __init__(self, config_path: str):
        self.config_path: str = config_path
        self.bot_token: str = ''
        self.provider_token: str = ''
        self.db_path = None
        self.orders_chat_id = None
        self.support_chat_id = None
        self.org_bot_token = ""

        if os.path.exists(config_path):
            self.__load_settings()
        else:
            self.create_file()
            raise FileNotFoundError("Создан файл config.json, заполните его")

    def create_file(self):
        with open(self.config_path, 'w', encoding='utf-8') as file:
            file.write(CONFIG_TEMPLATE)

    def update_orders_chat(self, chat_id: int):
        self.orders_chat_id = chat_id
        self.__save_setting('orders_chat_id', chat_id)

    def update_support_chat(self, chat_id: int):
        self.support_chat_id = chat_id
        self.__save_setting('support_chat_id', chat_id)

    def __load_settings(self):
        with open(self.config_path, 'r', encoding='utf-8') as file:
            config = json.loads(file.read())
            self.bot_token = config['tg_bot_token']
            if not self.bot_token:
                raise ValueError("Токен бота не указан. Добавьте его в config.json")
            self.provider_token = config['provider_token']
            if not self.provider_token:
                raise ValueError("Токен платежей не указан. Добавьте его в config.json")
            self.db_path = config["db_path"]
            self.orders_chat_id = config["orders_chat_id"]
            self.support_chat_id = config["support_chat_id"]
            self.org_bot_token = config["org_bot_token"]

    def __save_setting(self, setting_name: str, setting):
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            data[setting_name] = setting
            with open(self.config_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4)
        except Exception as exception:
            raise exception


class CachedImages:
    def __init__(self, db: DataBase, start_path: str, bot_name: str):
        self.bot_name = bot_name
        self.db = db
        self.START_PATH = start_path
        # db.execute("DELETE FROM img_cache where bot_name= ?", bot_name, commit=True)

    async def send_cached_img(self, message: Message, path: str, caption: str,
                              reply_markup: InlineKeyboardMarkup,
                              parse_mode=ParseMode.HTML,
                              message_edit=True):
        res_path = self.START_PATH + path
        img_id = self.db.execute("SELECT img_id FROM img_cache WHERE path = ? AND bot_name = ?", res_path,
                                 self.bot_name, fetch="one")
        if not img_id:
            res = res_path
        else:
            res, = img_id
        if message_edit:
            if not img_id:
                try:
                    message = await message.edit_media(
                        InputMediaPhoto(InputFile(res), caption=caption, parse_mode=parse_mode),
                        reply_markup=reply_markup)
                except Exception as e:
                    print('Message is not modified')
                    print(e)
            else:
                try:
                    message = await message.edit_media(InputMediaPhoto(res, caption=caption, parse_mode=parse_mode),
                                                       reply_markup=reply_markup)
                except Exception as e:
                    print('Message is not modified')
                    print(e)
        else:
            if not img_id:
                message = await message.answer_photo(InputFile(res), caption=caption, reply_markup=reply_markup,
                                                     parse_mode=parse_mode)
            else:
                message = await message.answer_photo(res, caption=caption, reply_markup=reply_markup,
                                                     parse_mode=parse_mode)
        if not img_id:
            self.db.execute("INSERT INTO img_cache (path, img_id, bot_name) VALUES (?, ?, ?) ", res_path,
                            message.photo[-1].file_id, self.bot_name, commit=True)
        return message
