import asyncio
import datetime as dt
from io import BytesIO
from typing import Union

import aiogram
import qrcode
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ParseMode, Message, CallbackQuery, ChatActions, ReplyKeyboardMarkup
from magic_filter import F

import constants
from bot_create import users_bot, dp, config
from create_db import data_base
from fsm import menu_fsm
from fsm.menu_fsm import LetteringState
from fsm.registration_fsm import GreetingState
from markups import menu_markups
from markups.menu_markups import menu_markup
from middleware import antispam, admins
from texts import menu_texts


async def any_message_menu_respond(message: types.Message, state: FSMContext):
    await GreetingState.block.set()
    await users_bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    await asyncio.sleep(0.5)
    await state.finish()
    await message.answer(menu_texts.RESPOND_TEXT,
                         reply_markup=menu_markup)


async def send_menu_on_update(update: Union[Message, CallbackQuery], state: FSMContext):
    await state.finish()
    if isinstance(update, CallbackQuery):
        message = update.message
    else:
        message = update

    await message.answer(menu_texts.MENU_TEXT,
                         reply_markup=menu_markups.menu_markup)


async def generate_qr_code(message: types.Message, state: FSMContext):
    payload = message.chat.id
    # payload = deep_linking.encode_payload(f'{message.chat.id}')
    link = f'https://t.me/{config.admin_bot_username}?start={payload}'
    image = qrcode.make(link)
    with BytesIO() as buffer:
        image.save(buffer)
        with BytesIO(buffer.getvalue()) as photo:
            await message.answer_photo(photo)


async def show_profile(update: types.Message | types.CallbackQuery):
    text, price = menu_texts.get_profile_text(data_base, update.from_user.id)
    markup = None
    if price:
        markup = menu_markups.start_order_markup
    else:
        text += '\nКорзина пуста'
    if isinstance(update, types.CallbackQuery):
        await update.message.edit_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)
    else:
        await update.answer(text, reply_markup=markup, parse_mode=ParseMode.HTML)


async def show_help(message: types.Message):
    await message.answer(menu_texts.FAQ_TEXT,
                         reply_markup=menu_markups.help_markup,
                         parse_mode=ParseMode.HTML,
                         disable_web_page_preview=True)


async def show_promotions(message: types.Message):
    await message.answer(menu_texts.MENU_PROMOTIONS_TEXT,
                         parse_mode=ParseMode.HTML)


async def support_input(message: types.Message):
    await message.answer(menu_texts.HELP_INPUT_REQUEST,
                         reply_markup=ReplyKeyboardMarkup(
                             resize_keyboard=True
                         ).add(menu_markups.CANCEL_BUTTON)
                         )
    await menu_fsm.SupportState.input_wait.set()


async def cancel(message: types.Message, state: FSMContext):
    await message.answer(menu_texts.BACK_TO_MENU_TEXT,
                         reply_markup=menu_markups.menu_markup)
    await state.finish()


async def support_sent(message: types.Message, state: FSMContext):
    user = message.from_user
    support_request_sent = data_base.get_last_support_request_time(user.id)
    now = dt.datetime.now(tz=constants.TZ)
    if support_request_sent and now < support_request_sent + constants.SUPPORT_TIMEDELTA:
        ans_text = menu_texts.TOO_FREQUENTLY_TEMPLATE.format(constants.SUPPORT_TIMEDELTA_ACCUSATIVE_STR)
        await message.answer(ans_text,
                             reply_markup=menu_markups.menu_markup)
    else:
        await users_bot.send_message(chat_id=config.support_chat_id,
                                     text=menu_texts.TO_SUPPORT_MESSAGE_TEMPLATE.format(user.username, user.url,
                                                                                        message.text))
        await message.answer(menu_texts.HELP_MESSAGE_SENT,
                             reply_markup=menu_markups.menu_markup)
        data_base.add_transaction(constants.TransactionTypes.SUPPORT_REQUEST.value,
                                  message.from_user.id, None, message.text)
    await state.finish()


async def promo_respond(message: types.Message):
    await message.answer(menu_texts.PROMO_INPUT_REQUEST,
                         reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(menu_markups.CANCEL_BUTTON))
    await menu_fsm.PromoState.input_wait.set()


@antispam.set_limits(60, 10, 3600)
async def promo_input(message: types.Message, state: FSMContext):
    promo = message.text
    error_code = data_base.use_promo(message.from_user.id, promo)
    if error_code == 0:
        money_got, = data_base.execute("SELECT money FROM promo WHERE name = ?", promo, fetch="one")
        await message.answer(menu_texts.PROMO_SUCCESSFULLY_ACTIVATED_TEMPLATE.format(money_got),
                             reply_markup=menu_markups.menu_markup)
        await state.finish()
    elif error_code == 2:
        await message.answer(menu_texts.PROMO_ALREADY_USED,
                             reply_markup=menu_markups.menu_markup)
        await state.finish()
    else:
        await message.answer(menu_texts.PROMO_DOESNT_EXISTS,
                             reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(menu_markups.CANCEL_BUTTON)
                             )


async def show_shop_temp_message(message: types.Message):
    await message.answer(menu_texts.STORE_TEMP_TEXT)


async def clear_markup(message: Message):
    await message.answer('клавиатура очищена', reply_markup=types.ReplyKeyboardRemove())


@admins.check(level=3)
async def set_orders_chat(message: Message):
    config.update_orders_chat(message.chat.id)
    await message.answer('чат для заказов установлен')


@admins.check(level=3)
async def set_support_chat(message: Message):
    config.update_support_chat(message.chat.id)
    await message.answer('чат поддержки установлен')


# Рассылка
@admins.check(level=3)
async def lettering_respond(message: Message):
    markup = ReplyKeyboardMarkup()
    markup.add(menu_markups.CANCEL_BUTTON)
    await message.answer("Пожалуйста, введите текст рассылки.",
                         reply_markup=markup)
    await LetteringState.get_text.set()


@admins.check(level=3)
async def lettering_get(message: types.Message, state: FSMContext):
    text = message.text
    markup = ReplyKeyboardMarkup()
    markup.add("Подтвердить")
    markup.add(menu_markups.CANCEL_BUTTON)
    await message.answer("Так будет выглядеть текст рассылки:\n\n" +
                         text,
                         reply_markup=markup,
                         parse_mode=ParseMode.HTML)

    await state.update_data(lettering_text=text)
    await LetteringState.lettering_confirmation.set()


@admins.check(level=3)
async def lettering_start_lettering(message, state: FSMContext):
    data = await state.get_data()
    text = data["lettering_text"]

    users_data = data_base.execute("SELECT tg_id FROM users", fetch=True)
    await message.answer(f"Рассылка начата для {len(users_data)} пользователей. "
                         f"Она займёт {constants.LETTERING_PERIOD * len(users_data)} секунд.",
                         reply_markup=menu_markups.menu_markup)
    users_delivered = 0
    for telegram_id, in users_data:
        await asyncio.sleep(constants.LETTERING_PERIOD)
        try:
            await users_bot.send_message(chat_id=telegram_id, text=text, parse_mode=ParseMode.HTML)
        except Exception as e:
            print(e)
        else:
            users_delivered += 1
    await asyncio.sleep(constants.LETTERING_PERIOD)
    await message.answer(f"Рассылка отправлена {users_delivered} пользователям. ",
                         reply_markup=menu_markups.menu_markup)
    await state.finish()


@admins.check(level=3)
async def send_message(message: types.Message):
    args = message.text.split()
    if len(args) < 3:
        await message.answer(f'Не корректная команда: "{message.text}"\n'
                             f'формат: "/m [userid] [message]"')
        return

    user = data_base.get_user_info(args[1], 'tg_id')
    if user is None:
        await message.answer(f'пользователь {args[1]} не найден')
        return

    text_start = message.text.find(args[2])
    text = message.text[text_start:]
    try:
        await message.bot.send_message(args[1], 'Сообщение от администратора:\n' + text)
        await message.answer('Сообщение отправлено')
    except aiogram.utils.exceptions.ChatNotFound:
        await message.answer('Произошла ошибка: чат не найден, сообщение НЕ отправлено')


def register_menu_handlers():
    dp.register_message_handler(set_orders_chat, commands=['orderschat'])
    dp.register_message_handler(set_support_chat, commands=['supportchat'])
    dp.register_message_handler(clear_markup, commands=['clear'])
    dp.register_message_handler(send_message, commands=['m'])
    # Рассылка
    dp.register_message_handler(lettering_respond,
                                text="Рассылка",
                                state=None)
    dp.register_message_handler(send_menu_on_update,
                                state=menu_fsm.LetteringState.get_text,
                                text=menu_texts.CANCEL_TEXT)
    dp.register_message_handler(lettering_get,
                                state=menu_fsm.LetteringState.get_text)
    dp.register_message_handler(lettering_start_lettering,
                                state=menu_fsm.LetteringState.lettering_confirmation,
                                text="Подтвердить")
    dp.register_message_handler(send_menu_on_update,
                                state=menu_fsm.LetteringState.lettering_confirmation,
                                text=menu_texts.CANCEL_TEXT)

    dp.register_message_handler(send_menu_on_update,
                                F.from_user.func(lambda user: data_base.user_registered(user.id)),
                                state="*",
                                commands=['start'])
    dp.register_message_handler(show_profile,
                                text=menu_texts.MENU_PROFILE_BUTTON_TEXT,
                                state="*")
    dp.register_message_handler(show_help,
                                text=menu_texts.MENU_HELP_BUTTON_TEXT,
                                state="*")
    dp.register_message_handler(show_promotions,
                                text=menu_texts.MENU_PROMOTIONS_BUTTON_TEXT,
                                state="*")
    dp.register_message_handler(support_input,
                                text=menu_texts.HELP_BUTTON_TEXT,
                                state=None)
    dp.register_message_handler(cancel,
                                text=menu_texts.CANCEL_TEXT,
                                state=menu_fsm.SupportState.input_wait)
    dp.register_message_handler(cancel,
                                text=menu_texts.BACK_BUTTON_TEXT,
                                state=None)
    dp.register_message_handler(support_sent,
                                state=menu_fsm.SupportState.input_wait)
    dp.register_message_handler(cancel,
                                text=menu_texts.CANCEL_TEXT,
                                state=menu_fsm.PromoState.input_wait)
    dp.register_message_handler(promo_respond,
                                state=None,
                                text=menu_texts.MENU_PROMO_BUTTON_TEXT)
    dp.register_message_handler(promo_input,
                                state=menu_fsm.PromoState.input_wait)
    dp.register_message_handler(show_shop_temp_message,
                                state=None,
                                text=menu_texts.MENU_STORE_BUTTON_TEXT)
    # Обязательно оставить в конце, чтобы отвечал на остальные сообщения
    dp.register_message_handler(any_message_menu_respond,
                                F.from_user.func(lambda user: data_base.user_registered(user.id)),
                                state=None)
