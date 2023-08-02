from aiogram.utils.callback_data import CallbackData
from texts.admin_menu_texts import BACK_TO_MENU_BUTTON_TEXT
from texts import admin_stuff_redactor_texts as asr_texts

FIELD_EDIT = CallbackData(asr_texts.FIELD_EDIT_CALLBACK, 'field')
FIELD_NAME_CALLBACK = FIELD_EDIT.new('name')
FIELD_PRICE_CALLBACK = FIELD_EDIT.new('price')
FIELD_CATEGORY_CALLBACK = FIELD_EDIT.new('category')
FIELD_DESCRIPTION_CALLBACK = FIELD_EDIT.new('description')
FIELD_COUNT_CALLBACK = FIELD_EDIT.new('count')
FIELD_IMAGE_CALLBACK = FIELD_EDIT.new('image')
FIELD_SHOW_CALLBACK = FIELD_EDIT.new('show')

BACK_CALLBACK = CallbackData(BACK_TO_MENU_BUTTON_TEXT, 'back_from')
BACK_FIELDS_CALLBACK = BACK_CALLBACK.new('staff_fields')
BACK_STAFF_CALLBACK = BACK_CALLBACK.new('staff')
BACK_CATEGORIES_CALLBACK = BACK_CALLBACK.new('staff_categories')
BACK_CATEGORY_CALLBACK = BACK_CALLBACK.new('staff_categories')

DELETE_CALLBACK = CallbackData(asr_texts.DELETE_CALLBACK_TEXT)
NOT_DELETE_CALLBACK = CallbackData(asr_texts.NOT_DELETE_CALLBACK_TEXT)
