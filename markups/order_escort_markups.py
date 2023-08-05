from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from texts import order_escort_texts
from callbacks import order_escort_callbacks as OEC
from constants import OrderStates


def select_markup(next_state, order_data: dict):
    order_id = order_data['order_id']
    user_id = order_data['user_id']
    match next_state:
        case OrderStates.ORDER_ACCEPTED.value:
            return get_order_accepted_markup(order_id, user_id)
        case OrderStates.ORDER_COOKING.value:
            return get_order_cooking_markup(order_id, user_id)
        case OrderStates.ORDER_DONE.value:
            return get_order_done_markup(order_id, user_id)
        case OrderStates.ORDER_DELIVERY.value:
            return get_order_delivery_markup(order_id, user_id)
        case OrderStates.ORDER_DELIVERED.value:
            return get_order_delivered_markup(order_id, user_id)
        case OrderStates.ORDER_ISSUED.value:
            return get_order_delivery_markup(order_id, user_id)


def yes_no_markup(prev_markup: InlineKeyboardMarkup, order_data: dict, current_state: int):
    state_name = ''
    for button in prev_markup.inline_keyboard[0]:
        if button['callback_data'].split(':')[-1] == order_data['state']:
            state_name = button.text
    markup = InlineKeyboardMarkup().add(
        InlineKeyboardButton(state_name + '?', callback_data='empty'))
    markup.add(InlineKeyboardButton('да', callback_data=OEC.YES_CB.new(order_id=order_data['order_id'],
                                                                       user_id=order_data['user_id'],
                                                                       state=current_state)),
               InlineKeyboardButton('Нет', callback_data=OEC.NO_CB.new(order_id=order_data['order_id'],
                                                                       user_id=order_data['user_id'],
                                                                       state=current_state)))
    return markup


def get_order_accepted_markup(order_id: int, user_id: int):
    button = InlineKeyboardButton(order_escort_texts.ORDER_ACCEPTED_BUTTON_TEXT,
                                  callback_data=OEC.ORDER_STATE_CB.new(order_id=order_id,
                                                                       user_id=user_id,
                                                                       state=OrderStates.ORDER_ACCEPTED.value))
    return InlineKeyboardMarkup().add(button)


def get_order_cooking_markup(order_id: int, user_id: int):
    button = InlineKeyboardButton(order_escort_texts.ORDER_COOKING_BUTTON_TEXT,
                                  callback_data=OEC.ORDER_STATE_CB.new(order_id=order_id,
                                                                       user_id=user_id,
                                                                       state=OrderStates.ORDER_COOKING.value)
                                  )
    return InlineKeyboardMarkup().add(button)


def get_order_done_markup(order_id: int, user_id: int):
    button = InlineKeyboardButton(order_escort_texts.ORDER_DONE_BUTTON_TEXT,
                                  callback_data=OEC.ORDER_STATE_CB.new(order_id=order_id,
                                                                       user_id=user_id,
                                                                       state=OrderStates.ORDER_DONE.value))
    return InlineKeyboardMarkup().add(button)


def get_order_delivery_markup(order_id: int, user_id: int):
    button = InlineKeyboardButton(order_escort_texts.ORDER_DELIVERY_BUTTON_TEXT,
                                  callback_data=OEC.ORDER_STATE_CB.new(order_id=order_id,
                                                                       user_id=user_id,
                                                                       state=OrderStates.ORDER_DELIVERY.value))
    button2 = InlineKeyboardButton(order_escort_texts.ORDER_ISSUED_BUTTON_TEXT,
                                   callback_data=OEC.ORDER_STATE_CB.new(order_id=order_id,
                                                                        user_id=user_id,
                                                                        state=OrderStates.ORDER_ISSUED.value))
    return InlineKeyboardMarkup().add(button, button2)


def get_order_delivered_markup(order_id: int, user_id: int):
    button = InlineKeyboardButton(order_escort_texts.ORDER_DELIVERED_BUTTON_TEXT,
                                  callback_data=OEC.ORDER_STATE_CB.new(order_id=order_id,
                                                                       user_id=user_id,
                                                                       state=OrderStates.ORDER_DELIVERED.value))
    return InlineKeyboardMarkup().add(button)
