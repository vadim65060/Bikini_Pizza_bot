from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton as IKB, ReplyKeyboardMarkup
from texts import admin_stuff_redactor_texts as asr_texts, admin_menu_texts
from callbacks import admin_stuff_redactor_callbacks as asr_callbacks
from texts.admin_menu_texts import BACK_TO_MENU_BUTTON_TEXT

TO_STAFF_REDACTOR_MACKUP = ReplyKeyboardMarkup(resize_keyboard=True)
TO_STAFF_REDACTOR_MACKUP.add(admin_menu_texts.MENU_STUFF_REDACTOR_BUTTON_TEXT)

STUFF_FIELDS_MARKUP = InlineKeyboardMarkup()
STUFF_FIELDS_MARKUP.add(IKB(text=asr_texts.FIELD_NAME_TEXT,
                            callback_data=asr_callbacks.FIELD_NAME_CB),
                        IKB(text=asr_texts.FIELD_PRICE_TEXT,
                            callback_data=asr_callbacks.FIELD_PRICE_CB),
                        IKB(text=asr_texts.SIZES_EDIT_TEXT,
                            callback_data=asr_callbacks.SIZES_EDIT_CB))

STUFF_FIELDS_MARKUP.add(IKB(text=asr_texts.FIELD_CATEGORY_TEXT,
                            callback_data=asr_callbacks.FIELD_CATEGORY_CB),
                        IKB(text=asr_texts.FIELD_DESCRIPTION_TEXT,
                            callback_data=asr_callbacks.FIELD_DESCRIPTION_CB))
STUFF_FIELDS_MARKUP.add(IKB(text=asr_texts.FIELD_IMAGE_TEXT,
                            callback_data=asr_callbacks.FIELD_IMAGE_CB),
                        IKB(text=asr_texts.FIELD_SHOW_TEXT,
                            callback_data=asr_callbacks.FIELD_SHOW_CB))
STUFF_FIELDS_MARKUP.add(IKB(text=asr_texts.BACK_BUTTON_TEXT,
                            callback_data=asr_callbacks.BACK_FIELDS_CB))

STUFF_SELECT_MARKUP = InlineKeyboardMarkup().add(IKB(text=asr_texts.BACK_BUTTON_TEXT,
                                                     callback_data=asr_callbacks.BACK_STAFF_CB))
CATEGORY_SELECT_MARKUP = InlineKeyboardMarkup(IKB(text=BACK_TO_MENU_BUTTON_TEXT,
                                                  callback_data=asr_callbacks.BACK_CATEGORIES_CB))

DELETE_MARKUP = InlineKeyboardMarkup()
DELETE_MARKUP.add(IKB(text=asr_texts.DELETE_TEXT, callback_data=asr_texts.DELETE_CALLBACK_TEXT),
                  IKB(text=asr_texts.NOT_DELETE_TEXT, callback_data=asr_texts.NOT_DELETE_CALLBACK_TEXT))

CATEGORY_FIELDS_MARKUP = InlineKeyboardMarkup()
CATEGORY_FIELDS_MARKUP.add(IKB(text=asr_texts.FIELD_NAME_TEXT,
                               callback_data=asr_callbacks.FIELD_NAME_CB),
                           IKB(text=asr_texts.FIELD_DESCRIPTION_TEXT,
                               callback_data=asr_callbacks.FIELD_DESCRIPTION_CB),
                           IKB(text=asr_texts.FIELD_IMAGE_TEXT,
                               callback_data=asr_callbacks.FIELD_IMAGE_CB))
CATEGORY_FIELDS_MARKUP.add(IKB(text=asr_texts.BACK_BUTTON_TEXT,
                               callback_data=asr_callbacks.BACK_CATEGORY_CB))

NO_SIZES_MARKUP = InlineKeyboardMarkup()
NO_SIZES_MARKUP.add(IKB(asr_texts.ADD_SIZE_TEXT, callback_data=asr_callbacks.ADD_SIZE_CB.new()),
                    IKB(asr_texts.BACK_BUTTON_TEXT, callback_data=asr_callbacks.BACK_SELECT_SIZES))


def get_sizes_markup(sizes_info):
    markup = InlineKeyboardMarkup()
    for size_id, size in sizes_info:
        markup.insert(IKB(size, callback_data=asr_callbacks.SELECT_SIZE_CB.new(size_id=size_id)))
    markup.add(IKB(asr_texts.ADD_SIZE_TEXT, callback_data=asr_callbacks.ADD_SIZE_CB.new()),
               IKB(asr_texts.BACK_BUTTON_TEXT, callback_data=asr_callbacks.BACK_SELECT_SIZES))
    return markup


def get_size_edit_markup(size_id: int):
    markup = InlineKeyboardMarkup()
    markup.add(IKB(asr_texts.SIZE_FIELD_SIZE_TEXT, callback_data=asr_callbacks.EDIT_SIZE_CB.new(size_id=size_id)),
               IKB(asr_texts.FIELD_PRICE_TEXT, callback_data=asr_callbacks.EDIT_SIZE_PRICE_CB.new(size_id=size_id)),
               IKB(asr_texts.DELETE_TEXT, callback_data=asr_callbacks.DELETE_SIZE_CB.new(size_id=size_id)))
    markup.add(IKB(asr_texts.BACK_BUTTON_TEXT, callback_data=asr_callbacks.BACK_SIZE_EDITOR))
    return markup


def get_delete_size_markup(size_id: int):
    markup = InlineKeyboardMarkup()
    markup.add(
        IKB(asr_texts.DELETE_TEXT, callback_data=asr_callbacks.CONFIRM_DELETE_SIZE_CB.new(size_id=size_id, yes=1)),
        IKB(asr_texts.NOT_DELETE_TEXT,
            callback_data=asr_callbacks.CONFIRM_DELETE_SIZE_CB.new(size_id=size_id, yes=0)))
    return markup
