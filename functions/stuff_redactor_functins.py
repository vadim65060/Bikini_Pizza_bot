from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from markups import admin_menu_markups
from markups import admin_staff_redactor_markups as asr_markups
from admin_bot_create import data_base, store_cached_imgs
from texts import admin_menu_texts, admin_stuff_redactor_texts as asr_texts


async def exit_check(message: Message, state: FSMContext):
    if message.text and message.text.casefold() == admin_menu_texts.MENU_STUFF_REDACTOR_BUTTON_TEXT.casefold():
        await message.answer(admin_menu_texts.MENU_STUFF_REDACTOR_BUTTON_TEXT,
                             reply_markup=admin_menu_markups.stuff_redactor_markup)
        await state.finish()
        return True
    return False


async def print_edited_stuff(message: Message, state: FSMContext, markup=asr_markups.STUFF_FIELDS_MARKUP,
                             edit: bool = False):
    data = await state.get_data()
    stuff_id = data['stuff_id']
    if edit:
        message = data['edit_stuff']
    data = data_base.get_stuff_info(stuff_id, 'name, stuff_category_id, price, description, count, img_path, show')
    name, category_id, price, description, count, image, show = data
    category_name, = data_base.get_stuff_category_info(category_id, 'name')
    text = asr_texts.STUFF_FIELDS_PRINT.format(name, price, category_name, category_id, description,
                                               count)
    text += asr_texts.STUFF_SHOW_FIELD_PRINT.format(bool(show))
    new_message = await store_cached_imgs.send_cached_img(message, image, text,
                                                          reply_markup=markup,
                                                          message_edit=edit)
    if not edit:
        await state.update_data({'edit_stuff': new_message})


async def print_category(message: Message, state: FSMContext, markup, edit: bool = False):
    data = await state.get_data()
    category_id = data['category_id']
    if edit:
        message = data['edit_category']
    data = data_base.get_stuff_category_info(category_id, 'name, description, img_path')
    name, description, image = data
    text = asr_texts.CATEGORY_FIELDS_PRINT.format(name, description, image)
    new_message = await store_cached_imgs.send_cached_img(message, image, text, reply_markup=markup, message_edit=edit)
    if not edit:
        await state.update_data({'edit_category': new_message})


async def print_stuff_categories(message: Message, state: FSMContext):
    categories = data_base.get_stuff_categories()
    categories_ids = []
    text = asr_texts.STUFF_EDIT_SELECT_CATEGORY_TEXT
    for category in categories:
        text += f'{category[0]}) {category[1]}\n'
        categories_ids.append(category[0])
    await state.update_data({'categories': categories_ids})
    await message.answer(text, reply_markup=asr_markups.TO_STAFF_REDACTOR_MACKUP)


async def print_stuff_by_category(message: Message, state: FSMContext):
    stuffs = data_base.get_stuff_by_category_id(message.text, 'id, name')
    stuffs_ids = []
    text = asr_texts.STUFF_EDIT_SELECT_STUFF_TEXT
    for stuff in stuffs:
        text += f'{stuff[0]}) {stuff[1]}\n'
        stuffs_ids.append(stuff[0])
    await state.update_data({'stuffs': stuffs_ids})
    await message.answer(text, reply_markup=asr_markups.STUFF_SELECT_MARKUP)
