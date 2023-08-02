from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton as IKB, ReplyKeyboardMarkup
from texts import admin_stuff_redactor_texts as asr_texts, admin_menu_texts
from callbacks import admin_stuff_redactor_callbacks as asr_callbacks
from texts.admin_menu_texts import BACK_TO_MENU_BUTTON_TEXT

TO_STAFF_REDACTOR_MACKUP = ReplyKeyboardMarkup(resize_keyboard=True)
TO_STAFF_REDACTOR_MACKUP.add(admin_menu_texts.MENU_STUFF_REDACTOR_BUTTON_TEXT)

STUFF_FIELDS_MARKUP = InlineKeyboardMarkup()
STUFF_FIELDS_MARKUP.add(IKB(text=asr_texts.FIELD_NAME_TEXT,
                            callback_data=asr_callbacks.FIELD_NAME_CALLBACK),
                        IKB(text=asr_texts.FIELD_PRICE_TEXT,
                            callback_data=asr_callbacks.FIELD_PRICE_CALLBACK),
                        IKB(text=asr_texts.FIELD_COUNT_TEXT,
                            callback_data=asr_callbacks.FIELD_COUNT_CALLBACK))
STUFF_FIELDS_MARKUP.add(IKB(text=asr_texts.FIELD_CATEGORY_TEXT,
                            callback_data=asr_callbacks.FIELD_CATEGORY_CALLBACK),
                        IKB(text=asr_texts.FIELD_DESCRIPTION_TEXT,
                            callback_data=asr_callbacks.FIELD_DESCRIPTION_CALLBACK))
STUFF_FIELDS_MARKUP.add(IKB(text=asr_texts.FIELD_IMAGE_TEXT,
                            callback_data=asr_callbacks.FIELD_IMAGE_CALLBACK),
                        IKB(text=asr_texts.FIELD_SHOW_TEXT,
                            callback_data=asr_callbacks.FIELD_SHOW_CALLBACK))
STUFF_FIELDS_MARKUP.add(IKB(text=asr_texts.BACK_BUTTON_TEXT,
                            callback_data=asr_callbacks.BACK_FIELDS_CALLBACK))
STUFF_SELECT_MARKUP = InlineKeyboardMarkup()
STUFF_SELECT_MARKUP.add(IKB(text=asr_texts.BACK_BUTTON_TEXT,
                            callback_data=asr_callbacks.BACK_STAFF_CALLBACK))
CATEGORY_SELECT_MARKUP = InlineKeyboardMarkup(IKB(text=BACK_TO_MENU_BUTTON_TEXT,
                                                  callback_data=asr_callbacks.BACK_CATEGORIES_CALLBACK))

DELETE_MARKUP = InlineKeyboardMarkup()
DELETE_MARKUP.add(IKB(text=asr_texts.DELETE_TEXT, callback_data=asr_texts.DELETE_CALLBACK_TEXT),
                  IKB(text=asr_texts.NOT_DELETE_TEXT, callback_data=asr_texts.NOT_DELETE_CALLBACK_TEXT))

CATEGORY_FIELDS_MARKUP = InlineKeyboardMarkup()
CATEGORY_FIELDS_MARKUP.add(IKB(text=asr_texts.FIELD_NAME_TEXT,
                               callback_data=asr_callbacks.FIELD_NAME_CALLBACK),
                           IKB(text=asr_texts.FIELD_DESCRIPTION_TEXT,
                               callback_data=asr_callbacks.FIELD_DESCRIPTION_CALLBACK),
                           IKB(text=asr_texts.FIELD_IMAGE_TEXT,
                               callback_data=asr_callbacks.FIELD_IMAGE_CALLBACK))
CATEGORY_FIELDS_MARKUP.add(IKB(text=asr_texts.BACK_BUTTON_TEXT,
                               callback_data=asr_callbacks.BACK_CATEGORY_CALLBACK))
