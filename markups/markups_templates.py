from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from callbacks import callbacks_templates


def get_yes_no_markup(payload: str):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Да', callback_data=callbacks_templates.YES_NO_CB.new(payload=payload, yes=1)),
               InlineKeyboardButton('Нет', callback_data=callbacks_templates.YES_NO_CB.new(payload=payload, yes=0)))
    return markup
