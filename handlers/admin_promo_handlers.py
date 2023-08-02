import datetime as dt
import constants

from aiogram.types import Message, ParseMode
from aiogram.dispatcher import FSMContext

from markups import admin_menu_markups
from texts import admin_menu_texts, org_promo_texts
from admin_bot_create import admin_dp, data_base
from middleware import admins
from fsm.admin_menu_fsm import PromoState
from functions import org_menu_functions

from validator_collection import checkers


@admins.check(level=3)
async def input_promo(message: Message, state: FSMContext):
    await message.answer(org_promo_texts.HOW_CREATE_PROMO_TEXT,
                         reply_markup=admin_menu_markups.random_promo_markup)
    await PromoState.choose_promo.set()


@admins.check(level=3)
async def choose_promo(message: Message, state: FSMContext):
    if message.text.casefold() == admin_menu_texts.BACK_TO_MENU_BUTTON_TEXT.casefold():
        await message.answer(admin_menu_texts.BACK_TO_MENU_TEXT,
                             reply_markup=admin_menu_markups.admin_menu_markup)
        await state.finish()
        return

    promo_code = message.text
    if promo_code.casefold() == org_promo_texts.RANDOM_PROMO_BUTTON_TEXT.casefold():
        promo_code = org_menu_functions.get_generate_promo_code(6)
    if data_base.get_promo_id(promo_code):
        await message.answer(org_promo_texts.PROMO_ALREADY_EXISTS_TEXT)
        return
    await state.update_data({'promo_code': promo_code})
    await message.answer(org_promo_texts.NUM_POINTS_PROMO_TEXT,
                         reply_markup=admin_menu_markups.back_to_menu_markup)
    await PromoState.num_points.set()


@admins.check(level=3)
async def num_points_promo(message: Message, state: FSMContext):
    if message.text.casefold() == admin_menu_texts.BACK_TO_MENU_BUTTON_TEXT.casefold():
        await message.answer(admin_menu_texts.BACK_TO_MENU_TEXT,
                             reply_markup=admin_menu_markups.admin_menu_markup)
        await state.finish()
        return

    if not checkers.is_integer(message.text, minimum=1):
        await message.answer(org_promo_texts.NUM_POINTS_ERROR_PROMO_TEXT)
        return
    num_points = int(message.text)
    await state.update_data({'num_points': num_points})
    await message.answer(org_promo_texts.NUM_USES_PROMO_TEXT,
                         reply_markup=admin_menu_markups.infinite_uses_promo_markup)
    await PromoState.num_uses.set()


@admins.check(level=3)
async def num_uses_promo(message: Message, state: FSMContext):
    if message.text.casefold() == admin_menu_texts.BACK_TO_MENU_BUTTON_TEXT.casefold():
        await message.answer(admin_menu_texts.BACK_TO_MENU_TEXT,
                             reply_markup=admin_menu_markups.admin_menu_markup)
        await state.finish()
        return

    if message.text.casefold() == org_promo_texts.INFINITE_USES_BUTTON_TEXT.casefold():
        num_uses = -1
    else:
        if not checkers.is_integer(message.text, minimum=1):
            await message.answer(org_promo_texts.NUM_USES_ERROR_PROMO_TEXT)
            return
        num_uses = int(message.text)
    await state.update_data({'num_uses': num_uses})
    await message.answer(org_promo_texts.PERIOD_PROMO_TEXT,
                         reply_markup=admin_menu_markups.back_to_menu_markup)
    await PromoState.period.set()


@admins.check(level=3)
async def period_promo(message: Message, state: FSMContext):
    if message.text.casefold() == admin_menu_texts.BACK_TO_MENU_BUTTON_TEXT.casefold():
        await message.answer(admin_menu_texts.BACK_TO_MENU_TEXT,
                             reply_markup=admin_menu_markups.admin_menu_markup)
        await state.finish()
        return

    if not checkers.is_integer(message.text[:-1], minimum=1) or (message.text[-1] not in constants.PERIOD_TYPES):
        await message.answer(org_promo_texts.PERIOD_ERROR_PROMO_TEXT)
        return
    period_time = int(message.text[:-1])
    period_type = message.text[-1]

    dt_registered = dt.datetime.now(constants.TZ)
    if period_type == constants.PERIOD_TYPES[0]:
        dt_ends = dt_registered + dt.timedelta(hours=period_time)
    else:
        dt_ends = dt_registered + dt.timedelta(days=period_time)

    time_registered = org_menu_functions.get_string_datetime(dt_registered)
    time_ends = org_menu_functions.get_string_datetime(dt_ends)
    data = await state.get_data()
    name = data['promo_code']
    money = data['num_points']
    can_use = data['num_uses']
    data_base.add_promo(name, money, can_use, time_registered, time_ends, message.from_user.id)
    await message.answer(org_promo_texts.PROMO_ADDED_TEMPLATE.format(name, money)
                         + org_menu_functions.get_promo_added_text(can_use, period_time, period_type),
                         parse_mode=ParseMode.HTML)
    await message.answer(admin_menu_texts.BACK_TO_MENU_TEXT,
                         reply_markup=admin_menu_markups.admin_menu_markup)
    await state.finish()


def register_org_promo_handlers():
    admin_dp.register_message_handler(input_promo,
                                      text=admin_menu_texts.MENU_CREATE_PROMO_BUTTON_TEXT,
                                      state="*")
    admin_dp.register_message_handler(choose_promo,
                                      state=PromoState.choose_promo)
    admin_dp.register_message_handler(num_points_promo,
                                      state=PromoState.num_points)
    admin_dp.register_message_handler(num_uses_promo,
                                      state=PromoState.num_uses)
    admin_dp.register_message_handler(period_promo,
                                      state=PromoState.period)
