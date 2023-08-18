from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State
from aiogram.types import Message, CallbackQuery, ContentTypes
from validator_collection import checkers

import constants
import handlers.stuff_redactor.admin_staff_sizes_edit_handlers
from callbacks import admin_stuff_redactor_callbacks as asr_callbacks
from fsm.admin_staff_redactor_fsm import StuffEditState
from functions.stuff_redactor_functins import exit_check, print_edited_stuff, print_stuff_categories, \
    print_stuff_by_category
from middleware import admins
from admin_bot_create import admin_dp, data_base
from texts import admin_menu_texts, admin_stuff_redactor_texts as asr_texts


async def field_update(message: Message, state: FSMContext, field_name: str, field_value: str | int, data_update=True):
    if data_update:
        data = await state.get_data()
        stuff_id = data.get('stuff_id')
        data_base.update_stuff(message.from_user.id, field_name, stuff_id, field_value)
    await StuffEditState.select_field.set()
    await print_edited_stuff(message, state, edit=True)


@admins.check(level=2)
async def print_edit_stuff_categories(message: Message, state: FSMContext):
    await print_stuff_categories(message, state)
    await StuffEditState.select_stuff_category.set()


@admins.check(level=2)
async def select_edit_stuff_categories(message: Message, state: FSMContext):
    if await exit_check(message, state):
        return

    data = await state.get_data()
    categories_ids: list = data['categories']
    if not checkers.is_integer(message.text, minimum=0) or categories_ids.index(int(message.text)) is ValueError:
        await message.answer(asr_texts.INCORRECT_INPUT_TEXT)
        return

    await print_stuff_by_category(message, state)
    await StuffEditState.select_stuff.set()


@admins.check(level=2)
async def select_edit_stuff(message: Message, state: FSMContext):
    if await exit_check(message, state):
        return

    data = await state.get_data()
    stuffs_ids: list = data['stuffs']
    if not checkers.is_integer(message.text, minimum=0) or stuffs_ids.index(int(message.text)) is ValueError:
        await message.answer(asr_texts.INCORRECT_INPUT_TEXT)
        return

    await state.update_data({'stuff_id': int(message.text)})
    await StuffEditState.select_field.set()
    await print_edited_stuff(message, state)


@admins.check(level=2)
async def edit_stuff_name(message: Message, state: FSMContext):
    if await exit_check(message, state):
        return

    name = message.text
    if data_base.get_stuff_info_by_name(name, 'id'):
        await message.answer(asr_texts.STUFF_ALREADY_EXISTS_TEXT)
        return

    await field_update(message, state, 'name', name)


@admins.check(level=2)
async def edit_stuff_price(message: Message, state: FSMContext):
    if await exit_check(message, state):
        return

    price = message.text
    if not checkers.is_integer(price, minimum=0):
        await message.answer(asr_texts.INCORRECT_INPUT_TEXT)
        return

    await field_update(message, state, 'price', price)


@admins.check(level=2)
async def edit_stuff_count(message: Message, state: FSMContext):
    if await exit_check(message, state):
        return

    count = message.text
    if not checkers.is_integer(count, minimum=0):
        await message.answer(asr_texts.INCORRECT_INPUT_TEXT)
        return

    await field_update(message, state, 'count', count)


@admins.check(level=2)
async def edit_stuff_category(message: Message, state: FSMContext):
    if await exit_check(message, state):
        return

    category_name = message.text
    category_id = data_base.get_stuff_category_id(category_name)
    if not category_id:
        await message.answer(asr_texts.INCORRECT_INPUT_TEXT)
        return
    category_id, = category_id

    await field_update(message, state, 'stuff_category_id', category_id)


@admins.check(level=2)
async def edit_stuff_description(message: Message, state: FSMContext):
    if await exit_check(message, state):
        return

    await field_update(message, state, 'description', message.text)


@admins.check(level=2)
async def edit_stuff_image(message: Message, state: FSMContext):
    if await exit_check(message, state):
        return
    data = await state.get_data()
    stuff_id = data['stuff_id']
    name, img_path = data_base.get_stuff_info(stuff_id, 'name, img_path')
    data_base.delete_cache_img(constants.STORE_PATH + img_path)
    await message.photo[-1].download(destination_file=constants.STORE_PATH + img_path)
    await field_update(message, state, 'img_path', img_path, data_update=False)


async def edit_stuff_show(message: Message, state: FSMContext):
    if await exit_check(message, state):
        return

    data = await state.get_data()
    stuff_id = data['stuff_id']
    show, = data_base.get_stuff_info(stuff_id, 'show')
    if show == 1:
        show = 0
    else:
        show = 1
    await field_update(message, state, 'show', show)


@admins.check(level=2)
async def print_selected_field(callback_query: CallbackQuery, state: FSMContext):
    callback = callback_query.data
    text: str
    new_state: State
    match callback:
        case asr_callbacks.FIELD_NAME_CB:
            text = asr_texts.STUFF_NAME_UPDATE_TEXT
            new_state = StuffEditState.edit_field_name

        case asr_callbacks.FIELD_PRICE_CB:
            text = asr_texts.STUFF_PRICE_UPDATE_TEXT
            new_state = StuffEditState.edit_field_price

        case asr_callbacks.FIELD_COUNT_CB:
            text = asr_texts.STUFF_COUNT_UPDATE_TEXT
            new_state = StuffEditState.edit_field_count

        case asr_callbacks.FIELD_CATEGORY_CB:
            text = asr_texts.STUFF_CATEGORY_UPDATE_TEXT
            new_state = StuffEditState.edit_field_category

        case asr_callbacks.FIELD_DESCRIPTION_CB:
            text = asr_texts.STUFF_DESCRIPTION_UPDATE_TEXT
            new_state = StuffEditState.edit_field_description

        case asr_callbacks.FIELD_IMAGE_CB:
            text = asr_texts.STUFF_IMAGE_UPDATE_TEXT
            new_state = StuffEditState.edit_field_image

        case asr_callbacks.FIELD_SHOW_CB:
            await edit_stuff_show(callback_query.message, state)
            return
        case asr_callbacks.SIZES_EDIT_CB:
            await handlers.stuff_redactor.admin_staff_sizes_edit_handlers.start_sizes_edit(callback_query, state)
            return
        case _:
            return
    await callback_query.answer(text)
    await new_state.set()


# async def back_on_fields_select(callback_query: CallbackQuery, state: FSMContext):
#     await callback_query.message.delete()
async def activate_back_button(callback_query: CallbackQuery, state: FSMContext):
    callback = callback_query.data
    new_state: State
    match callback:
        case asr_callbacks.BACK_FIELDS_CB:
            new_state = StuffEditState.select_stuff
        case asr_callbacks.BACK_STAFF_CB:
            new_state = StuffEditState.select_stuff_category
        case asr_callbacks.BACK_CATEGORIES_CB:
            return
        case asr_callbacks.BACK_SELECT_SIZES:
            await print_edited_stuff(callback_query.message, state)
            await callback_query.message.delete()
            return
        case asr_callbacks.BACK_SIZE_EDITOR:
            await handlers.stuff_redactor.admin_staff_sizes_edit_handlers.print_staff_sizes(callback_query, state)
            return
        case _:
            return
    await callback_query.message.delete()
    await new_state.set()


def register_admin_staff_update_handlers():
    admin_dp.register_message_handler(print_edit_stuff_categories,
                                      text=admin_menu_texts.REDACTOR_STAFF_UPDATE_BUTTON_TEXT,
                                      state='*')
    admin_dp.register_message_handler(select_edit_stuff_categories,
                                      state=StuffEditState.select_stuff_category)
    admin_dp.register_message_handler(select_edit_stuff,
                                      state=StuffEditState.select_stuff)

    admin_dp.register_callback_query_handler(print_selected_field,
                                             asr_callbacks.FIELD_EDIT.filter(),
                                             state=StuffEditState.select_field)
    admin_dp.register_message_handler(edit_stuff_name,
                                      state=StuffEditState.edit_field_name)
    admin_dp.register_message_handler(edit_stuff_price,
                                      state=StuffEditState.edit_field_price)
    admin_dp.register_message_handler(edit_stuff_count,
                                      state=StuffEditState.edit_field_count)
    admin_dp.register_message_handler(edit_stuff_category,
                                      state=StuffEditState.edit_field_category)
    admin_dp.register_message_handler(edit_stuff_description,
                                      state=StuffEditState.edit_field_description)
    admin_dp.register_message_handler(edit_stuff_image, content_types=ContentTypes.PHOTO,
                                      state=StuffEditState.edit_field_image)

    admin_dp.register_callback_query_handler(activate_back_button,
                                             asr_callbacks.BACK_CB.filter(),
                                             state=StuffEditState.all_states)
