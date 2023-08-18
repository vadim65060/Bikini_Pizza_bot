from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State
from aiogram.types import Message, CallbackQuery, ContentTypes
from aiogram.utils.callback_data import CallbackData
from validator_collection import checkers

import constants
from callbacks import admin_stuff_redactor_callbacks as asr_callbacks
from fsm.admin_staff_redactor_fsm import StuffEditState
from functions.stuff_redactor_functins import exit_check
from middleware import admins
from admin_bot_create import admin_dp, data_base as db, store_cached_imgs
from texts import admin_menu_texts, admin_stuff_redactor_texts as asr_texts
from markups import admin_staff_redactor_markups as asr_markups


@admins.check(level=2)
async def start_sizes_edit(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    staff_id = data['stuff_id']
    sizes_ids = db.get_sizes_info_by_staff_id(staff_id, 'id')
    if sizes_ids:
        await print_staff_sizes(callback, state)
    else:
        await answer_no_sized_stuff(callback, state)


async def answer_no_sized_stuff(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_caption(asr_texts.SIZES_NOT_FOUND, reply_markup=asr_markups.NO_SIZES_MARKUP)


@admins.check(level=2)
async def print_staff_sizes(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    stuff_id = data['stuff_id']
    sizes = db.get_sizes_info_by_staff_id(stuff_id, 'id, size')
    await callback.message.edit_reply_markup(asr_markups.get_sizes_markup(sizes))


@admins.check(level=2)
async def print_sizes_editor(update: CallbackQuery | Message, state: FSMContext | None, callback_data: dict):
    size_id = callback_data['size_id']
    if state:
        await state.update_data({'size_id': size_id})
    size_data = db.get_from_stuff_size(size_id, 'size, price')
    text = asr_texts.STUFF_SIZE_PRINT.format(size_data[0], size_data[1])
    markup = asr_markups.get_size_edit_markup(size_id)
    await StuffEditState.select_field.set()
    if isinstance(update, CallbackQuery):
        await update.message.edit_caption(text, reply_markup=markup)
    elif state:
        data = await state.get_data()
        staff_id = data['stuff_id']
        img_path = db.get_stuff_img_path(staff_id)
        await store_cached_imgs.send_cached_img(update, img_path, text, markup,
                                                message_edit=False)
    else:
        await update.answer(text, reply_markup=markup)


@admins.check(level=2)
async def get_new_size(callback: CallbackQuery):
    await StuffEditState.edit_size.set()
    await callback.answer(asr_texts.GET_SIZE_TEXT)


@admins.check(level=2)
async def set_new_size(message: Message, state: FSMContext):
    data = await state.get_data()
    size_id = data['size_id']
    db.update_stuff_size(message.from_user.id, 'size', size_id, message.text)
    await print_sizes_editor(message, state, {'size_id': size_id})


@admins.check(level=2)
async def get_new_price(callback: CallbackQuery):
    await StuffEditState.edit_size_price.set()
    await callback.answer(asr_texts.STUFF_PRICE_UPDATE_TEXT)


@admins.check(level=2)
async def set_new_price(message: Message, state: FSMContext):
    data = await state.get_data()
    size_id = data['size_id']
    price = message.text
    if not checkers.is_integer(price, minimum=0):
        await message.answer(asr_texts.INCORRECT_INPUT_TEXT)
        return

    db.update_stuff_size(message.from_user.id, 'price', size_id, price)
    await print_sizes_editor(message, state, {'size_id': size_id})


@admins.check(level=2)
async def confirm_delete(callback: CallbackQuery, callback_data: dict):
    size_id = callback_data['size_id']
    await callback.message.edit_reply_markup(asr_markups.get_delete_size_markup(size_id))


@admins.check(level=2)
async def cancel_delete(callback: CallbackQuery, callback_data: dict):
    await print_sizes_editor(callback, None, callback_data)


@admins.check(level=2)
async def delete_size(callback: CallbackQuery, state: FSMContext, callback_data: dict):
    db.delete_stuff_size(callback.from_user.id, callback_data['size_id'])
    await start_sizes_edit(callback, state)


async def create_size(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    stuff_id = data['stuff_id']
    db.create_stuff_size(callback.from_user.id, stuff_id, 'new size', 9999)
    await print_staff_sizes(callback, state)


def register_admin_size_edit_handlers():
    admin_dp.register_callback_query_handler(print_sizes_editor,
                                             asr_callbacks.SELECT_SIZE_CB.filter(),
                                             state=StuffEditState.select_field)
    admin_dp.register_callback_query_handler(create_size, asr_callbacks.ADD_SIZE_CB.filter(),
                                             state=StuffEditState.select_field)

    admin_dp.register_callback_query_handler(get_new_size,
                                             asr_callbacks.EDIT_SIZE_CB.filter(),
                                             state=StuffEditState.select_field)
    admin_dp.register_message_handler(set_new_size, state=StuffEditState.edit_size)

    admin_dp.register_callback_query_handler(get_new_price,
                                             asr_callbacks.EDIT_SIZE_PRICE_CB.filter(),
                                             state=StuffEditState.select_field)
    admin_dp.register_message_handler(set_new_price, state=StuffEditState.edit_size_price)

    admin_dp.register_callback_query_handler(confirm_delete, asr_callbacks.DELETE_SIZE_CB.filter(),
                                             state=StuffEditState.select_field)
    admin_dp.register_callback_query_handler(cancel_delete, asr_callbacks.CONFIRM_DELETE_SIZE_CB.filter(yes='0'),
                                             state=StuffEditState.select_field)
    admin_dp.register_callback_query_handler(delete_size, asr_callbacks.CONFIRM_DELETE_SIZE_CB.filter(yes='1'),
                                             state=StuffEditState.select_field)
