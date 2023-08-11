from aiogram.utils.callback_data import CallbackData
from texts.admin_menu_texts import BACK_TO_MENU_BUTTON_TEXT
from texts import admin_stuff_redactor_texts as asr_texts

FIELD_EDIT = CallbackData(asr_texts.FIELD_EDIT_CALLBACK, 'field')
FIELD_NAME_CB = FIELD_EDIT.new('name')
FIELD_PRICE_CB = FIELD_EDIT.new('price')
FIELD_CATEGORY_CB = FIELD_EDIT.new('category')
FIELD_DESCRIPTION_CB = FIELD_EDIT.new('description')
FIELD_COUNT_CB = FIELD_EDIT.new('count')
FIELD_IMAGE_CB = FIELD_EDIT.new('image')
FIELD_SHOW_CB = FIELD_EDIT.new('show')
SIZES_EDIT_CB = FIELD_EDIT.new('sizes')

BACK_CB = CallbackData(BACK_TO_MENU_BUTTON_TEXT, 'back_from')
BACK_FIELDS_CB = BACK_CB.new('staff_fields')
BACK_STAFF_CB = BACK_CB.new('staff')
BACK_CATEGORIES_CB = BACK_CB.new('staff_categories')
BACK_CATEGORY_CB = BACK_CB.new('staff_categories')

DELETE_CB = CallbackData(asr_texts.DELETE_CALLBACK_TEXT)
NOT_DELETE_CB = CallbackData(asr_texts.NOT_DELETE_CALLBACK_TEXT)
