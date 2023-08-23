from functools import lru_cache

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup

from database.db_funcs import DataBase
from texts import order_texts
from callbacks import order_callbacks

back_markup = ReplyKeyboardMarkup(resize_keyboard=True).add(order_texts.BACK_TEXT)

pickup_markup = InlineKeyboardMarkup()
pickup_markup.add(InlineKeyboardButton(order_texts.PICKUP_TEXT, callback_data=order_callbacks.PICKUP_CB))


def get_order_markup(pickup):
    if pickup:
        delivery_button = InlineKeyboardButton(order_texts.DELIVERY_TEXT, callback_data=order_callbacks.DELIVERY_CB)
    else:
        delivery_button = InlineKeyboardButton(order_texts.PICKUP_TEXT, callback_data=order_callbacks.PICKUP_CB)

    order_markup = InlineKeyboardMarkup()
    order_markup.add(InlineKeyboardButton(order_texts.USE_BALLS_BUTTON_TEXT, callback_data=order_callbacks.USE_BALL_CB),
                     InlineKeyboardButton(order_texts.ADD_COMMENT_TEXT, callback_data=order_callbacks.ADD_COMMENT_CB),
                     InlineKeyboardButton(order_texts.CANCEL_BUTTON_TEXT, callback_data=order_callbacks.CANCEL_CB))
    order_markup.add(InlineKeyboardButton(order_texts.DELIVERY_ZONE_BUTTON_TEXT, url=order_texts.DELIVERY_ZONE_URL),
                     delivery_button)
    if not pickup:
        order_markup.add(
            InlineKeyboardButton(order_texts.EDIT_ADDRESS_BUTTON_TEXT, callback_data=order_callbacks.DELIVERY_CB))
    order_markup.add(InlineKeyboardButton(order_texts.ORDER_BUTTON_TEXT, callback_data=order_callbacks.ORDER_CB))
    return order_markup


@lru_cache()
def get_pickup_addresses(db: DataBase):
    pickup_addresses_markup = InlineKeyboardMarkup()
    shops = db.get_shops()
    for shop in shops:
        button = InlineKeyboardButton(shop[1], callback_data=order_callbacks.SHOP_ADDRESSES_CB.new(shop_id=shop[0]))
        pickup_addresses_markup.add(button)

    return pickup_addresses_markup
