from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from callbacks.store_callbacks import STORE_CATEGORY_CB


def get_store_markup(categories):
    markup = InlineKeyboardMarkup()
    for category_id, name in categories:
        markup.add(InlineKeyboardButton(name, callback_data=STORE_CATEGORY_CB.new(category_id=category_id)))
    return markup
