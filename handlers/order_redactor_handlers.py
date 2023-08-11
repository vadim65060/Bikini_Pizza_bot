from aiogram.types import CallbackQuery
from aiogram.utils.callback_data import CallbackData

from bot_create import dp
from callbacks import order_redactor_callbacks
from callbacks.menu_callbacks import BASKET_EDIT_CB
from create_db import data_base as db
from handlers.menu_handlers import show_profile
from markups import order_redactor_markups
from texts import order_redactor_texts
from texts.menu_texts import get_user_basket_text


async def print_order_edit(callback: CallbackQuery):
    booked_list = db.booked_list(callback.from_user.id)
    markup = order_redactor_markups.get_redactor_markup(booked_list)
    text, _ = get_user_basket_text(booked_list)
    if text == '':
        text = order_redactor_texts.BASKET_EMPTY_TEXT
    await callback.message.edit_text(text, reply_markup=markup)


async def edit_order(callback: CallbackQuery, callback_data: dict):
    edit_count = int(callback_data['plus'])
    staff_id = int(callback_data['staff_id'])
    size_id = callback_data['size_id'] if callback_data['size_id'] != 'None' else None
    if edit_count < 0:
        db.delete_user_purchase(callback.from_user.id, staff_id, size_id, abs(edit_count))
    else:
        db.add_user_purchase(callback.from_user.id, staff_id, size_id, edit_count)
    await print_order_edit(callback)


async def exit_edit_mode(callback: CallbackQuery):
    await show_profile(callback)


def register_order_redactor_handlers():
    dp.register_callback_query_handler(exit_edit_mode, CallbackData(order_redactor_callbacks.BACK_CB).filter())
    dp.register_callback_query_handler(print_order_edit, CallbackData(BASKET_EDIT_CB).filter())
    dp.register_callback_query_handler(edit_order, order_redactor_callbacks.BASKET_EDIT_CB.filter())
