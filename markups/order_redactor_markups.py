from texts import order_redactor_texts
from callbacks import order_redactor_callbacks
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup


def get_redactor_markup(booked_list):
    markup = InlineKeyboardMarkup()
    for stuff_id, size_id, name, price, size, count in booked_list:
        if size_id is None:
            size_id = 'None'
        markup.add(InlineKeyboardButton(order_redactor_texts.STAFF_SUBTRACT_TEXT,
                                        callback_data=order_redactor_callbacks.BASKET_EDIT_CB.new(staff_id=stuff_id,
                                                                                                  size_id=size_id,
                                                                                                  plus=-1)),
                   InlineKeyboardButton(name + (f' {size}' if size else ''), callback_data='staff'),
                   InlineKeyboardButton(order_redactor_texts.STAFF_ADD_TEXT,
                                        callback_data=order_redactor_callbacks.BASKET_EDIT_CB.new(staff_id=stuff_id,
                                                                                                  size_id=size_id,
                                                                                                  plus=1)))
    markup.add(InlineKeyboardButton(order_redactor_texts.BACK_TEXT, callback_data=order_redactor_callbacks.BACK_CB))
    return markup
