from typing import Union

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message, ParseMode, ReplyKeyboardMarkup
from magic_filter import F

import constants
from admin_bot_create import admin_dp, data_base
from fsm.admin_menu_fsm import TakeOutAccess
from functions import org_menu_functions
from handlers import admin_promo_handlers, admin_give_admin_handlers
from handlers.stuff_redactor import admin_category_update_handlers, admin_category_delete_handlers
from handlers.stuff_redactor import admin_stuff_create_handlers, admin_stuff_update_handlers
from handlers.stuff_redactor import admin_stuff_delete_handlers, admin_category_create_handlers
from markups import admin_menu_markups
from middleware import admins
from texts import admin_menu_texts, org_promo_texts


async def send_menu_on_update(update: Union[Message, CallbackQuery], state: Union[FSMContext, None]):
    if isinstance(update, CallbackQuery):
        message = update.message
    else:
        message = update
    await message.answer(admin_menu_texts.ADMIN_MENU_TEXT, reply_markup=admin_menu_markups.admin_menu_markup)
    await state.finish()


@admins.check(level=2)
async def open_steff_redactor(update: Union[Message, CallbackQuery], state: FSMContext):
    if isinstance(update, CallbackQuery):
        message = update.message
    else:
        message = update
    await message.answer(admin_menu_texts.ADMIN_MENU_TEXT, reply_markup=admin_menu_markups.stuff_redactor_markup)
    await state.finish()


@admins.check(level=3)
async def admins_list(message: Message, state: FSMContext):
    await message.answer(org_menu_functions.get_admin_list_text(data_base),
                         parse_mode=ParseMode.HTML)


@admins.check(level=3)
async def take_out_access_input(message: Message, state: FSMContext):
    await message.answer(admin_menu_texts.TAKE_OUT_ACCESS_USERNAME_INPUT_TEXT,
                         reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
                             admin_menu_texts.BACK_TO_MENU_BUTTON_TEXT))
    await TakeOutAccess.take_access_input.set()


@admins.check(level=3)
async def process_take_out_request(message: Message, state: FSMContext):
    username = message.text
    tg_id = data_base.get_user_id_by_username(username)
    if tg_id and data_base.have_admin_rights(tg_id, 1):
        data_base.execute("DELETE FROM admins WHERE tg_id = ?", tg_id, commit=True)
        data_base.add_transaction(constants.TransactionTypes.ADMIN_TAKE_OUT.value,
                                  message.from_user.id,
                                  tg_id, None)
        text = admin_menu_texts.TAKE_OUT_ACCESS_DONE_TEMPLATE.format(
            username if username and username[0] != "@" else username[1:])
    else:
        data_base.add_transaction(constants.TransactionTypes.ADMIN_TAKE_OUT.value,
                                  message.from_user.id,
                                  None, f"failed try to take access from {username}")
        text = admin_menu_texts.TAKE_OUT_ACCESS_NOT_FOUND_TEXT
    await message.answer(text + "\n\n" + admin_menu_texts.TAKE_OUT_ACCESS_USERNAME_INPUT_TEXT,
                         reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
                             admin_menu_texts.BACK_TO_MENU_BUTTON_TEXT),
                         parse_mode=ParseMode.HTML)
    await TakeOutAccess.take_access_input.set()


@admins.check(level=3)
async def show_promo_list(message: Message, state: FSMContext):
    promo_list = data_base.get_promo_list()
    counter = 1
    promo_list_text = ""
    texts = []
    for promo in promo_list:
        name, money, can_use, used, time_ends = promo
        promo_list_text += str(counter) + ". " \
                           + org_promo_texts.PROMO_TO_LIST_TEMPLATE.format(name, money) \
                           + org_menu_functions.get_promo_to_list_text(can_use, time_ends, used) + "\n\n"
        counter += 1
        if counter % 20 == 0:
            texts.append(promo_list_text)
            promo_list_text = ""
    if counter % 20 != 0:
        texts.append(promo_list_text)
    for text in texts:
        await message.answer(text, parse_mode=ParseMode.HTML)


def register_admin_menu_handlers():
    # org_merch_issuance_handlers.register_merch_issuance_handlers()
    admin_dp.register_message_handler(send_menu_on_update,
                                      text=admin_menu_texts.BACK_TO_MENU_BUTTON_TEXT,
                                      state="*")
    admin_dp.register_message_handler(send_menu_on_update,
                                      state="*",
                                      commands=['start'])
    admin_dp.register_message_handler(open_steff_redactor,
                                      text=admin_menu_texts.MENU_STUFF_REDACTOR_BUTTON_TEXT)
    admin_dp.register_message_handler(show_promo_list,
                                      text=admin_menu_texts.MENU_LIST_PROMO_BUTTON_TEXT)
    admin_dp.register_message_handler(admins_list,
                                      state="*",
                                      text=admin_menu_texts.MENU_ADMINS_LIST_BUTTON_TEXT)
    admin_dp.register_message_handler(take_out_access_input,
                                      text=admin_menu_texts.MENU_TAKE_AWAY_ACCESS_BUTTON_TEXT)
    admin_dp.register_message_handler(process_take_out_request,
                                      state=TakeOutAccess.take_access_input)
    admin_promo_handlers.register_org_promo_handlers()
    admin_stuff_create_handlers.register_admin_staff_create_handlers()
    admin_stuff_update_handlers.register_admin_staff_update_handlers()
    admin_stuff_delete_handlers.register_admin_staff_delete_handlers()
    admin_category_create_handlers.register_admin_staff_create_handlers()
    admin_category_update_handlers.register_admin_category_update_handlers()
    admin_give_admin_handlers.register_org_promo_handlers()
    admin_category_delete_handlers.register_admin_category_delete_handlers()
    admin_dp.register_message_handler(send_menu_on_update,
                                      F.from_user.func(lambda user: data_base.user_registered(user.id)),
                                      state=None)
