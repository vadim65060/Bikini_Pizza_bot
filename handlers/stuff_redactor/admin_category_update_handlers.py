from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State
from aiogram.types import Message, CallbackQuery, ContentTypes
from validator_collection import checkers

import constants
from callbacks import admin_stuff_redactor_callbacks as asr_callbacks
from fsm.admin_staff_redactor_fsm import CategoryEditState
from functions.stuff_redactor_functins import exit_check, print_category, print_stuff_categories
from markups.admin_staff_redactor_markups import CATEGORY_FIELDS_MARKUP
from middleware import admins
from admin_bot_create import admin_dp, data_base
from texts import admin_menu_texts, admin_stuff_redactor_texts as asr_texts


async def field_update(message: Message, state: FSMContext, field_name: str, field_value: str | int, data_update=True):
    if data_update:
        data = await state.get_data()
        category_id = data.get('category_id')
        data_base.update_stuff_category(message.from_user.id, field_name, category_id, field_value)
    await CategoryEditState.select_field.set()
    await print_category(message, state, CATEGORY_FIELDS_MARKUP, edit=True)


@admins.check(level=2)
async def print_edit_categories(message: Message, state: FSMContext):
    await print_stuff_categories(message, state)
    await CategoryEditState.select_category.set()


@admins.check(level=2)
async def select_edit_categories(message: Message, state: FSMContext):
    if await exit_check(message, state):
        return

    data = await state.get_data()
    categories_ids: list = data['categories']
    if not checkers.is_integer(message.text, minimum=0) or categories_ids.index(int(message.text)) is ValueError:
        await message.answer(asr_texts.INCORRECT_INPUT_TEXT)
        return

    await state.update_data({'category_id': int(message.text)})
    await print_category(message, state, CATEGORY_FIELDS_MARKUP)
    await CategoryEditState.select_field.set()


@admins.check(level=2)
async def edit_category_name(message: Message, state: FSMContext):
    if await exit_check(message, state):
        return

    name = message.text
    if data_base.get_category_id_by_name(name):
        await message.answer(asr_texts.STUFF_ALREADY_EXISTS_TEXT)
        return

    await field_update(message, state, 'name', name)


@admins.check(level=2)
async def edit_category_description(message: Message, state: FSMContext):
    if await exit_check(message, state):
        return

    await field_update(message, state, 'description', message.text)


@admins.check(level=2)
async def edit_category_image(message: Message, state: FSMContext):
    if await exit_check(message, state):
        return
    data = await state.get_data()
    category_id = data['category_id']
    name, img_path = data_base.get_stuff_category_info(category_id, 'name, img_path')
    data_base.delete_cache_img(constants.STORE_PATH + img_path)
    await message.photo[-1].download(destination_file=constants.STORE_PATH + img_path)
    await field_update(message, state, 'img_path', img_path, data_update=False)


@admins.check(level=2)
async def print_selected_field(callback_query: CallbackQuery, state: FSMContext):
    callback = callback_query.data
    text: str
    new_state: State
    match callback:
        case asr_callbacks.FIELD_NAME_CB:
            text = asr_texts.STUFF_NAME_UPDATE_TEXT
            new_state = CategoryEditState.edit_name

        case asr_callbacks.FIELD_DESCRIPTION_CB:
            text = asr_texts.STUFF_DESCRIPTION_UPDATE_TEXT
            new_state = CategoryEditState.edit_description

        case asr_callbacks.FIELD_IMAGE_CB:
            text = asr_texts.STUFF_IMAGE_UPDATE_TEXT
            new_state = CategoryEditState.edit_image

        case _:
            text = 'field_error\nвведи id категории'
            new_state = CategoryEditState.select_field
    await callback_query.answer(text)
    await new_state.set()


async def back_button(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.delete()
    await CategoryEditState.select_category.set()


def register_admin_category_update_handlers():
    admin_dp.register_message_handler(print_edit_categories,
                                      text=admin_menu_texts.REDACTOR_CATEGORY_UPDATE_BUTTON_TEXT,
                                      state='*')
    admin_dp.register_message_handler(select_edit_categories,
                                      state=CategoryEditState.select_category)

    admin_dp.register_callback_query_handler(print_selected_field,
                                             asr_callbacks.FIELD_EDIT.filter(),
                                             state=CategoryEditState.select_field)
    admin_dp.register_message_handler(edit_category_name,
                                      state=CategoryEditState.edit_name)
    admin_dp.register_message_handler(edit_category_description,
                                      state=CategoryEditState.edit_description)
    admin_dp.register_message_handler(edit_category_image, content_types=ContentTypes.PHOTO,
                                      state=CategoryEditState.edit_image)

    admin_dp.register_callback_query_handler(back_button,
                                             asr_callbacks.BACK_CB.filter(back_from='staff_categories'),
                                             state=CategoryEditState.select_field)
