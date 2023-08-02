from aiogram.types import ReplyKeyboardMarkup
from texts import org_scaner_texts, admin_menu_texts, org_promo_texts
from callbacks import org_menu_callbacks
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

admin_menu_markup = ReplyKeyboardMarkup(resize_keyboard=True)
admin_menu_markup.add(admin_menu_texts.MENU_STUFF_REDACTOR_BUTTON_TEXT)
admin_menu_markup.add(admin_menu_texts.MENU_CREATE_PROMO_BUTTON_TEXT,
                      admin_menu_texts.MENU_LIST_PROMO_BUTTON_TEXT)
admin_menu_markup.add(admin_menu_texts.MENU_TAKE_AWAY_ACCESS_BUTTON_TEXT)
admin_menu_markup.insert(admin_menu_texts.MENU_ADMINS_LIST_BUTTON_TEXT)
admin_menu_markup.insert(admin_menu_texts.MENU_GIVE_ACCESS_BUTTON_TEXT)

stuff_redactor_markup = ReplyKeyboardMarkup(resize_keyboard=True)
stuff_redactor_markup.add(admin_menu_texts.REDACTOR_STAFF_CREATE_BUTTON_TEXT,
                          admin_menu_texts.REDACTOR_STAFF_UPDATE_BUTTON_TEXT,
                          admin_menu_texts.REDACTOR_STAFF_DELETE_BUTTON_TEXT)
stuff_redactor_markup.add(admin_menu_texts.REDACTOR_CATEGORY_CREATE_BUTTON_TEXT,
                          admin_menu_texts.REDACTOR_CATEGORY_UPDATE_BUTTON_TEXT,
                          admin_menu_texts.REDACTOR_CATEGORY_DELETE_BUTTON_TEXT)
stuff_redactor_markup.add(admin_menu_texts.BACK_TO_MENU_BUTTON_TEXT)

back_to_menu_markup = ReplyKeyboardMarkup(resize_keyboard=True)
back_to_menu_markup.add(admin_menu_texts.BACK_TO_MENU_BUTTON_TEXT)

random_promo_markup = ReplyKeyboardMarkup(resize_keyboard=True)
random_promo_markup.add(org_promo_texts.RANDOM_PROMO_BUTTON_TEXT)
random_promo_markup.add(admin_menu_texts.BACK_TO_MENU_BUTTON_TEXT)

infinite_uses_promo_markup = ReplyKeyboardMarkup(resize_keyboard=True)
infinite_uses_promo_markup.add(org_promo_texts.INFINITE_USES_BUTTON_TEXT)
infinite_uses_promo_markup.add(admin_menu_texts.BACK_TO_MENU_BUTTON_TEXT)

yes_no_markup = InlineKeyboardMarkup()
yes_no_markup.add(InlineKeyboardButton(text=org_scaner_texts.YES_BUTTON_TEXT,
                                       callback_data=org_menu_callbacks.YES_NO_CALLBACK.new(1)),
                  InlineKeyboardButton(text=org_scaner_texts.NO_BUTTON_TEXT,
                                       callback_data=org_menu_callbacks.YES_NO_CALLBACK.new(0)))
