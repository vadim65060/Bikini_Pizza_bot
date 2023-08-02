from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, PhotoSize
from validator_collection import checkers

import constants
from fsm.admin_staff_redactor_fsm import StuffCreateState
from functions.stuff_redactor_functins import exit_check
from markups import admin_staff_redactor_markups as asr_markups
from middleware import admins
from admin_bot_create import admin_dp, data_base
from texts import admin_menu_texts, admin_stuff_redactor_texts as asr_texts
from markups.admin_menu_markups import stuff_redactor_markup


@admins.check(level=2)
async def input_stuff_create(message: Message, state: FSMContext):
    await message.answer(asr_texts.STUFF_NAME_UPDATE_TEXT,
                         reply_markup=asr_markups.TO_STAFF_REDACTOR_MACKUP)
    await StuffCreateState.set_name.set()


@admins.check(level=2)
async def set_stuff_name(message: Message, state: FSMContext):
    if await exit_check(message, state):
        return

    name = message.text
    if data_base.get_stuff_info_by_name(name, 'id'):
        await message.answer(asr_texts.STUFF_ALREADY_EXISTS_TEXT)
        return

    await state.update_data({'stuff_name': name})
    await message.answer(asr_texts.STUFF_PRICE_UPDATE_TEXT)
    await StuffCreateState.set_price.set()


@admins.check(level=2)
async def set_stuff_price(message: Message, state: FSMContext):
    if await exit_check(message, state):
        return

    price = message.text
    if not checkers.is_integer(price, minimum=0):
        await message.answer(asr_texts.INCORRECT_INPUT_TEXT)
        return

    await state.update_data({'stuff_price': price})
    await message.answer(asr_texts.STUFF_CATEGORY_UPDATE_TEXT)
    await StuffCreateState.set_category.set()


@admins.check(level=2)
async def set_stuff_category(message: Message, state: FSMContext):
    if await exit_check(message, state):
        return

    category_name = message.text
    category_id = data_base.get_stuff_category_id(category_name)
    if not category_id:
        await message.answer(asr_texts.INCORRECT_INPUT_TEXT)
        return

    category_id, = category_id
    await state.update_data({'stuff_category_id': category_id})
    await message.answer(asr_texts.STUFF_DESCRIPTION_UPDATE_TEXT)
    await StuffCreateState.set_description.set()


@admins.check(level=2)
async def set_stuff_description(message: Message, state: FSMContext):
    if await exit_check(message, state):
        return

    await state.update_data({'stuff_description': message.text})
    await message.answer(asr_texts.STUFF_COUNT_UPDATE_TEXT)
    await StuffCreateState.set_count.set()


@admins.check(level=2)
async def set_stuff_count(message: Message, state: FSMContext):
    if await exit_check(message, state):
        return

    count = message.text
    if not checkers.is_integer(count, minimum=0):
        await message.answer(asr_texts.INCORRECT_INPUT_TEXT)
        return

    await state.update_data({'stuff_count': count})
    await message.answer(asr_texts.STUFF_IMAGE_UPDATE_TEXT)
    await StuffCreateState.set_image.set()


@admins.check(level=2)
async def set_stuff_image(message: Message, state: FSMContext):
    if await exit_check(message, state):
        return

    await state.update_data({'stuff_image': message.photo[-1]})
    await print_created_stuff(message, state)
    await save_staff(message, state)
    await state.finish()


async def print_created_stuff(message: Message, state: FSMContext):
    data = await state.get_data()
    name = data['stuff_name']
    category_id = data['stuff_category_id']
    category_name = data_base.get_stuff_category_info(category_id, 'name')
    price = data['stuff_price']
    description = data['stuff_description']
    count = data['stuff_count']
    image = data['stuff_image']
    text = asr_texts.STUFF_FIELDS_PRINT.format(name, price, category_name, category_id, description,
                                               count)
    await message.answer_photo(image.file_id, text)


async def save_staff(message: Message, state: FSMContext):
    data = await state.get_data()
    name = data['stuff_name']
    category_id = data['stuff_category_id']
    price = data['stuff_price']
    description = data['stuff_description']
    count = data['stuff_count']
    image: PhotoSize = data['stuff_image']
    image_path = f'stuff/{name}_{image.file_id[-4:]}.png'
    await image.download(constants.STORE_PATH + image_path)
    data_base.add_stuff(message.from_user.id, category_id, name, description, price, image_path, count)
    await message.answer(asr_texts.STUFF_SAVE_TEXT, reply_markup=stuff_redactor_markup)


def register_admin_staff_create_handlers():
    admin_dp.register_message_handler(input_stuff_create,
                                      text=admin_menu_texts.REDACTOR_STAFF_CREATE_BUTTON_TEXT,
                                      state='*')
    admin_dp.register_message_handler(set_stuff_name,
                                      state=StuffCreateState.set_name)
    admin_dp.register_message_handler(set_stuff_price,
                                      state=StuffCreateState.set_price)
    admin_dp.register_message_handler(set_stuff_category,
                                      state=StuffCreateState.set_category)
    admin_dp.register_message_handler(set_stuff_description,
                                      state=StuffCreateState.set_description)
    admin_dp.register_message_handler(set_stuff_count,
                                      state=StuffCreateState.set_count)
    admin_dp.register_message_handler(set_stuff_image, content_types=types.ContentTypes.PHOTO,
                                      state=StuffCreateState.set_image)
