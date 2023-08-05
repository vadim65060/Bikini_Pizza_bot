from aiogram.types import CallbackQuery

from bot_create import dp, config, users_bot
from callbacks import order_escort_callbacks
from constants import OrderStates
from create_db import data_base as db
from markups import order_escort_markups as OEM
from texts import order_escort_texts


async def print_order(order_id: int):
    purchases = db.get_order_list(order_id)
    order_info = db.get_order_info(order_id, 'user_id, price, used_balls, delivery_cost, phone, address, comment')
    username, = db.get_user_info(order_info[0], 'username')
    text = order_escort_texts.get_profile_text(order_id, purchases, order_info, username)
    await users_bot.send_message(config.orders_chat_id, text,
                                 reply_markup=OEM.get_order_accepted_markup(order_id, order_info[0]))


async def accept_order(callback_data: dict):
    await users_bot.send_message(callback_data['user_id'], order_escort_texts.ORDER_ACCEPTED_USER_TEXT)


async def cooking_order(callback_data: dict):
    await users_bot.send_message(callback_data['user_id'], order_escort_texts.ORDER_COOKING_USER_TEXT)


async def done_order(callback_data: dict):
    await users_bot.send_message(callback_data['user_id'], order_escort_texts.ORDER_DONE_USER_TEXT)


async def delivery_order(callback_data: dict):
    await users_bot.send_message(callback_data['user_id'], order_escort_texts.ORDER_DELIVERY_USER_TEXT)


async def delivered_order(callback_data: dict):
    await users_bot.send_message(callback_data['user_id'], order_escort_texts.ORDER_DELIVERED_USER_TEXT)


async def issue_order(callback_data: dict):
    await users_bot.send_message(callback_data['user_id'], order_escort_texts.ORDER_ISSUED_USER_TEXT)


async def select_next_state(callback: CallbackQuery, callback_data: dict):
    match int(callback_data['state']):
        case OrderStates.ORDER_ACCEPTED.value:
            await accept_order(callback_data)
        case OrderStates.ORDER_COOKING.value:
            await cooking_order(callback_data)
        case OrderStates.ORDER_DONE.value:
            await done_order(callback_data)
        case OrderStates.ORDER_DELIVERY.value:
            await delivery_order(callback_data)
        case OrderStates.ORDER_DELIVERED.value:
            await delivered_order(callback_data)
        case OrderStates.ORDER_ISSUED.value:
            await issue_order(callback_data)
    await callback.message.edit_reply_markup(OEM.select_markup(int(callback_data['state']) + 1, callback_data))


async def back_state(callback: CallbackQuery, callback_data: dict):
    await callback.message.edit_reply_markup(OEM.select_markup(int(callback_data['state']), callback_data))


async def print_yes_no(callback: CallbackQuery, callback_data: dict):
    print(callback.data)
    await callback.message.edit_reply_markup(
        OEM.yes_no_markup(callback.message.reply_markup, callback_data, int(callback_data['state'])))


def register_order_escort_handlers():
    dp.register_callback_query_handler(back_state,
                                       order_escort_callbacks.NO_CB.filter())
    dp.register_callback_query_handler(select_next_state,
                                       order_escort_callbacks.YES_CB.filter())
    dp.register_callback_query_handler(print_yes_no,
                                       order_escort_callbacks.ORDER_STATE_CB.filter())
