from database.db_funcs import DataBase
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from callbacks.store_callbacks import ITEM_CB, BUY_NO_COLORS_SIZES_CB, BUY_COLORS_SIZES_CB, \
    BUY_CONFIRM_COLORS_SIZES_CB, BUY_CONFIRM_NO_COLORS_SIZES_CB

STORE_CATEGORIES_WITH_TUC_TEMPLATE = "Сейчас у тебя <b>{}</b> деняк.\n\nВыбери категорию:"

THING_NOT_FOUND_TEXT = "К сожалению, я не нашёл этот товар у себя на складе."
THING_HID = "Я тебе не покажу этот товар."

THING_NOT_ENOUGH_MONEY_TEXT = "К сожалению, твоих деняк не хватает на этот товар."
THING_HAS_BEEN_SOLD_TEXT = "К сожалению, ты не успел купить этот товар."
TRANSACTION_ERROR = "Произошла ошибка, транзакция не выполнена. Возможно, ты сможешь купить этот товар позже."

NO_RETURN_DISCLAIMER = "Учти, что забронированный мерч уже не получится разбронировать 🤭\n\n" + \
                       "В крайнем случае обращайтесь в техподдержку или к организаторам в магазине"


def get_size_color_thing_has_bought_text(db: DataBase, colors_sizes_id):
    stuff_id, size = db.get_stuff_sizes_texts_info(colors_sizes_id, "stuff_id, size")
    name, = db.get_stuff_info(stuff_id, "name")
    if not size:
        return f"{name} - хороший выбор. Поздравляю тебя с покупкой."
    return f"{name} {size} - хороший выбор. Поздравляю тебя с покупкой."


def get_no_size_color_thing_has_bought_text(db: DataBase, stuff_id):
    name, = db.get_stuff_info(stuff_id, "name")
    return f"{name} - хороший выбор. Поздравляю тебя с покупкой."


def get_thing_no_color_size_confirmation_text_markup(db: DataBase, stuff_id):
    data = db.get_stuff_info(stuff_id, "name, price, count, show")
    if not data:
        text = THING_NOT_FOUND_TEXT
        return text, None
    name, price, count, show = data
    if not show:
        text = THING_HID
        return text, None
    text = f"Добавить {name} за {price} в корзину?\n\n"
    markup = InlineKeyboardMarkup().add(
        InlineKeyboardButton("Подтвердить",
                             callback_data=BUY_CONFIRM_NO_COLORS_SIZES_CB.new(
                                 stuff_id=stuff_id))
    )
    return text, markup


def get_thing_color_size_confirmation_text_markup(db: DataBase, colors_sizes_id):
    data = db.get_stuff_sizes(colors_sizes_id, "stuff_id, price, size")
    stuff_id, price, size = data
    data = db.get_stuff_info(stuff_id, "name")
    name, = data
    text = f"Ты уверен, что хочешь приобрести предмет {name} "
    if size:
        text += f"размера {size} "
    text += f"за {price}RUB?\n\n"
    markup = InlineKeyboardMarkup().add(
        InlineKeyboardButton("Подтвердить",
                             callback_data=BUY_CONFIRM_COLORS_SIZES_CB.new(
                                 colors_sizes_id=colors_sizes_id)
                             )
    )
    return text, markup


def get_thing_color_size_text_markup(db: DataBase, stuff_id, tg_id):
    data = db.get_stuff_info(stuff_id, "name, description, price, show")
    markup = InlineKeyboardMarkup()
    if not data:
        text = THING_NOT_FOUND_TEXT
        return text, markup
    name, description, price, show = data
    if not show:
        text = THING_HID
        return text, markup
    combinations = db.get_all_size_combinations(stuff_id)
    count = db.get_stuff_count_num_by_stuff_id(stuff_id)

    if not description:
        description = ""
    else:
        description += "\n\n"
    text = f"<b>{name}</b>\n\n{description}" \
           f"Осталось: {count} шт.\nЦена: {price}i\n\n"
    if combinations:
        colors_sizes_id, color, size, count = combinations[0]
        if color is not None and size is None:
            text += f"Цвета:\n"
        elif color is None and size is not None:
            text += "<b>Размеры:</b>\n"
        elif color is not None and size is not None:
            text += "<b>Варианты:</b>\n"

    for colors_sizes_id, color, size, count in combinations:
        button_text = None
        if color is not None and size is None:
            text += f"{color} - {count} шт.\n"
            button_text = color
        elif color is None and size is not None:
            text += f"{size} - {count} шт.\n"
            button_text = size
        elif color is not None and size is not None:
            text += f"{color} {size} - шт.\n"
            button_text = f"{color} {size}"
        else:
            print("В stuff_size_colors есть (size, color) = (NULL, NULL)")
        if button_text:
            markup.insert(InlineKeyboardButton(
                button_text,
                callback_data=BUY_COLORS_SIZES_CB.new(colors_sizes_id=colors_sizes_id))
            )
    booked = db.how_many_stuff_booked(tg_id, stuff_id)
    if booked:
        text += f"\nВ корзине: {booked} шт."
    return text, markup


def get_thing_no_color_size_text_markup(db: DataBase, stuff_id, tg_id):
    data = db.get_stuff_info(stuff_id, "name, description, price, count, show")
    markup = InlineKeyboardMarkup()
    if not data:
        text = "К сожалению, товар не найден."
        return text, markup
    name, description, price, count, show = data
    if not show:
        text = "Товар скрыт"
        return text, markup
    if not description:
        description = ""
    else:
        description += "\n\n"
    text = f"<b>{name}</b>\n\n{description}" \
           f"Осталось: {count} шт.\nЦена: {price}"
    booked = db.how_many_stuff_booked(tg_id, stuff_id)
    if booked:
        text += f"\nВ корзине: {booked} шт."
    markup.add(InlineKeyboardButton("В корзину", callback_data=BUY_NO_COLORS_SIZES_CB.new(stuff_id=stuff_id)))
    return text, markup


def get_category_list_text_markup(db: DataBase, category_id, tg_id):
    description = db.get_category_description(category_id)
    stuff = db.get_stuff_by_category_id(category_id, "id, name, count, show, price")
    if not stuff:
        text = "К сожалению, эта категория пуста."
        return text, None
    markup = InlineKeyboardMarkup(row_width=2)
    text = description + "\n\n"
    for i, data in enumerate(stuff):
        stuff_id, name, count, show, price = data
        if count is None:
            with_colors_sizes = True
            # Поиск в таблице с распеределением по цветам и размерам
            count = db.get_stuff_count_num_by_stuff_id(stuff_id)
        else:
            with_colors_sizes = False
        indent = " " * (len(str(i + 1)) + 3)
        text += f"{i + 1}. <i>{name}</i>"
        price_output = False
        if with_colors_sizes:
            if show:
                # colors = db.get_all_colors_by_stuff_id(stuff_id)
                # if colors:
                #     text += f" — {price}"
                #     price_output = True
                #     text += f"\n{indent}(" + ", ".join([color for color_sizes_id, color in colors]) + ")"
                sizes = db.get_all_sizes_by_stuff_id(stuff_id)
                if sizes:
                    text += f"  (" + ", ".join([size for color_sizes_id, size in sizes]) + ")"
        if not price_output:
            text += f" — {price}"
        text += f"\n{indent}Осталось {count} шт.\n"
        booked = db.how_many_stuff_booked(tg_id, stuff_id)
        if booked:
            text += f"{indent}В корзине: {booked} шт.\n"
        text += "\n"
        markup.insert(InlineKeyboardButton(name, callback_data=ITEM_CB.new(stuff_id=stuff_id)))
    return text, markup
