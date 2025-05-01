from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ChatActions, ParseMode
from magic_filter import F

import constants
from bot_create import users_bot, dp, store_cached_imgs
from fsm.registration_fsm import GreetingState
from main import data_base
from markups.menu_markups import menu_markup
from texts import registration_texts


async def greetings(message: types.Message, state: FSMContext):
    await GreetingState.block.set()
    await users_bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    await store_cached_imgs.send_cached_img(message, constants.LOGO_PATH, registration_texts.HELLO_MESSAGE_TEXT,
                                            reply_markup=menu_markup, parse_mode=ParseMode.HTML, message_edit=False)
    data_base.add_user(message.from_user.id, message.from_user.username)
    await state.finish()


def register_registration_handlers():
    dp.register_message_handler(greetings,
                                ~F.from_user.func(lambda user: data_base.user_registered(user.id)),
                                state=None)
    dp.register_message_handler(greetings,
                                ~F.from_user.func(lambda user: data_base.user_registered(user.id)),
                                lambda s: s != GreetingState.block,
                                commands=['start'])
