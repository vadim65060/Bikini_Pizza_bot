from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery
from validator_collection import checkers

from functions.stuff_redactor_functins import exit_check, print_edited_stuff, print_stuff_categories, \
    print_stuff_by_category
from callbacks import admin_stuff_redactor_callbacks as asr_callbacks
from callbacks.org_menu_callbacks import YES_NO_CALLBACK
from fsm.admin_staff_redactor_fsm import StuffDeleteState
from markups import admin_menu_markups, admin_staff_redactor_markups as asr_markups
from middleware import admins
from admin_bot_create import admin_dp, data_base
from texts import admin_menu_texts, admin_stuff_redactor_texts as asr_texts


@admins.check(level=2)
async def print_delete_stuff_categories(message: Message, state: FSMContext):
    await print_stuff_categories(message, state)
    await StuffDeleteState.select_stuff_category.set()


@admins.check(level=2)
async def select_delete_stuff_categories(message: Message, state: FSMContext):
    if await exit_check(message, state):
        return

    data = await state.get_data()
    categories_ids: list = data['categories']
    if not checkers.is_integer(message.text, minimum=0) or categories_ids.index(int(message.text)) is ValueError:
        await message.answer(asr_texts.INCORRECT_INPUT_TEXT)
        return

    await print_stuff_by_category(message, state)
    await StuffDeleteState.select_stuff.set()


@admins.check(level=2)
async def select_delete_stuff(message: Message, state: FSMContext):
    if await exit_check(message, state):
        return

    data = await state.get_data()
    stuffs_ids: list = data['stuffs']
    if not checkers.is_integer(message.text, minimum=0) or stuffs_ids.index(int(message.text)) is ValueError:
        await message.answer(asr_texts.INCORRECT_INPUT_TEXT)
        return

    await state.update_data({'stuff_id': int(message.text)})
    await StuffDeleteState.delete_stuff.set()
    await print_edited_stuff(message, state, markup=asr_markups.DELETE_MARKUP)


@admins.check(level=2)
async def cancel_delete(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer(asr_texts.DELETE_STUFF_CANCEL_TEXT)
    await callback_query.message.delete()
    await StuffDeleteState.select_stuff.set()


@admins.check(level=2)
async def confirm_delete(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer(asr_texts.DELETE_CONFIRMATION)
    await callback_query.message.edit_reply_markup(admin_menu_markups.yes_no_markup)


@admins.check(level=2)
async def delete_stuff(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    stuff_id = data['stuff_id']
    data_base.delete_stuff(callback_query.from_user.id, stuff_id)
    await callback_query.message.delete()
    await callback_query.message.answer(asr_texts.STUFF_DELETED, reply_markup=admin_menu_markups.stuff_redactor_markup)
    await state.finish()


@admins.check(level=2)
async def cancel_confirmed_delete(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_reply_markup(asr_markups.DELETE_MARKUP)


def register_admin_staff_delete_handlers():
    admin_dp.register_message_handler(print_delete_stuff_categories,
                                      text=admin_menu_texts.REDACTOR_STAFF_DELETE_BUTTON_TEXT,
                                      state='*')
    admin_dp.register_message_handler(select_delete_stuff_categories,
                                      state=StuffDeleteState.select_stuff_category)
    admin_dp.register_message_handler(select_delete_stuff,
                                      state=StuffDeleteState.select_stuff)

    admin_dp.register_callback_query_handler(confirm_delete,
                                             asr_callbacks.DELETE_CALLBACK.filter(),
                                             state=StuffDeleteState.delete_stuff)
    admin_dp.register_callback_query_handler(cancel_delete,
                                             asr_callbacks.NOT_DELETE_CALLBACK.filter(),
                                             state=StuffDeleteState.delete_stuff)
    admin_dp.register_callback_query_handler(delete_stuff,
                                             YES_NO_CALLBACK.filter(decision='1'),
                                             state=StuffDeleteState.delete_stuff)
    admin_dp.register_callback_query_handler(cancel_confirmed_delete,
                                             YES_NO_CALLBACK.filter(decision='0'),
                                             state=StuffDeleteState.delete_stuff)
    # dp.register_callback_query_handler(activate_back_button,
    #                                    asr_callbacks.BACK_CALLBACK.filter(),
    #                                    state='*')
