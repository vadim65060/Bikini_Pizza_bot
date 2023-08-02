from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.reply_keyboard import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.callback_data import CallbackData

tuc_check_cd = CallbackData("tuc_check", "tg_id", "status")

in_tuc_markup = ReplyKeyboardMarkup(resize_keyboard=True,
                                    one_time_keyboard=True)


def get_tuc_check_inline_keyboard(tg_id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Он в ПК", callback_data=tuc_check_cd.new(tg_id=tg_id, status=1)))
    markup.add(InlineKeyboardButton("Он не в ПК", callback_data=tuc_check_cd.new(tg_id=tg_id, status=0)))
    return markup
