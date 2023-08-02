from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, PhotoSize

import constants
from fsm.admin_staff_redactor_fsm import CategoryCreateState
from functions.stuff_redactor_functins import exit_check
from markups import admin_staff_redactor_markups as asr_markups
from markups.admin_menu_markups import stuff_redactor_markup
from middleware import admins
from admin_bot_create import admin_dp, data_base
from texts import admin_menu_texts, admin_stuff_redactor_texts as asr_texts


@admins.check(level=2)
async def input_category_create(message: Message, state: FSMContext):
    await message.answer(asr_texts.CATEGORY_NAME_UPDATE_TEXT,
                         reply_markup=asr_markups.TO_STAFF_REDACTOR_MACKUP)
    await CategoryCreateState.set_name.set()


@admins.check(level=2)
async def set_category_name(message: Message, state: FSMContext):
    if await exit_check(message, state):
        return

    name = message.text
    if data_base.get_category_id_by_name(name):
        await message.answer(asr_texts.CATEGORY_ALREADY_EXISTS_TEXT)
        return

    await state.update_data({'category_name': name})
    await message.answer(asr_texts.CATEGORY_DESCRIPTION_UPDATE_TEXT)
    await CategoryCreateState.set_description.set()


@admins.check(level=2)
async def set_category_description(message: Message, state: FSMContext):
    if await exit_check(message, state):
        return

    await state.update_data({'category_description': message.text})
    await message.answer(asr_texts.CATEGORY_IMAGE_UPDATE_TEXT)
    await CategoryCreateState.set_image.set()


@admins.check(level=2)
async def set_category_image(message: Message, state: FSMContext):
    if await exit_check(message, state):
        return

    await state.update_data({'category_image': message.photo[-1]})
    await print_created_category(message, state)
    await save_category(message, state)
    await state.finish()


async def print_created_category(message: Message, state: FSMContext):
    data = await state.get_data()
    name = data['category_name']
    description = data['category_description']
    image = data['category_image']
    text = asr_texts.CATEGORY_FIELDS_PRINT.format(name, description)
    await message.answer_photo(image.file_id, text)


async def save_category(message: Message, state: FSMContext):
    data = await state.get_data()
    name = data['category_name']
    description = data['category_description']
    image: PhotoSize = data['category_image']
    image_path = f'categories/{name}_{image.file_id[-4:]}.png'
    await image.download(constants.STORE_PATH + image_path)
    data_base.add_stuff_category(message.from_user.id, name, description, image_path)
    await message.answer(asr_texts.CATEGORY_SAVE_TEXT, reply_markup=stuff_redactor_markup)


def register_admin_staff_create_handlers():
    admin_dp.register_message_handler(input_category_create,
                                      text=admin_menu_texts.REDACTOR_CATEGORY_CREATE_BUTTON_TEXT,
                                      state='*')
    admin_dp.register_message_handler(set_category_name,
                                      state=CategoryCreateState.set_name)
    admin_dp.register_message_handler(set_category_description,
                                      state=CategoryCreateState.set_description)
    admin_dp.register_message_handler(set_category_image, content_types=types.ContentTypes.PHOTO,
                                      state=CategoryCreateState.set_image)
