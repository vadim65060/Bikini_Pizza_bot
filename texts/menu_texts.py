# Тексты кнопок

from database.db_funcs import DataBase

MENU_PROFILE_BUTTON_TEXT = "Корзина"
MENU_STORE_BUTTON_TEXT = "Магазин"
MENU_PROMO_BUTTON_TEXT = "Ввести промокод"
MENU_HELP_BUTTON_TEXT = "Справка | Поддержка"

TOO_FREQUENTLY_TEMPLATE = \
    "Ты слишком общительный! Подожди {} и сможешь написать снова. А пока что возвращаю тебя в меню 😉"

HELP_BUTTON_TEXT = "Поддержка"
BACK_BUTTON_TEXT = "Назад"
CANCEL_TEXT = "Отмена"

# Тексты сообщений
RESPOND_TEXT = "Снизу есть кнопки меню, можешь их использовать."
MENU_TEXT = "Добро пожаловать в моё меню! Нажимай на кнопочки снизу 😎"

PROFILE_TEMPLATE = "Bikini coins: {}\n"
PROFILE_ERROR = "Произошла ошибка - тебя нет в базе данных"

ORDER_TEXT = "Заказать"
BASKET_EDIT_TEXT = "Редактировать"


def get_profile_text(db: DataBase, tg_id, print_sum=True):
    info = db.get_user_info(tg_id, "money")
    if not info:
        return PROFILE_ERROR, 0
    money, = info
    booked_list = db.booked_list(tg_id)
    text = PROFILE_TEMPLATE.format(money)
    if not booked_list:
        return text, 0
    text += "\n<b>Корзина</b>\n"
    basket_text, total_price = get_user_basket_text(booked_list, print_sum)
    text += basket_text
    return text, total_price


def get_user_basket_text(booked_list, print_sum=True):
    if not booked_list:
        return '', 0
    text = ''
    total_price = 0
    for stuff_id, stuff_sizes_id, name, price, size, count in booked_list:
        text += f"{name}"
        if size:
            text += f" {size}"
        text += f" {count}шт - {price * count}RUB\n"
        total_price += price * count
    if print_sum:
        text += f'---------------\n' \
                f'Итого: {total_price}RUB\n'
    return text, total_price


MESSAGE_CANT_BE_EDITED_TEXT = "Сообщение не редактируется :("

FAQ_TEXT = 'Пока тут ничего нет, задавай вопросы в поддержку'
HELP_INPUT_REQUEST = "Введи свой вопрос"
HELP_MESSAGE_SENT = "Запрос отправлен, возвращаю тебя в меню"
BACK_TO_MENU_TEXT = "Хорошо, возвращаю тебя в меню"
TO_SUPPORT_MESSAGE_TEMPLATE = "Пользователь: @{}\n" \
                              "Ссылка: {}\n" \
                              "Вопрос:\n{}"

PROMO_INPUT_REQUEST = "Если у тебя есть промокод, введи его сюда"
PROMO_SUCCESSFULLY_ACTIVATED_TEMPLATE = "Промокод на {} Bikini coins активирован! Возвращаю тебя в меню 😎"
PROMO_ALREADY_USED = "Ты уже вводил этот промокод, возвращаю тебя в меню"
PROMO_DOESNT_EXISTS = "Промокод недействителен 😕 Попробуй ещё раз!"

STORE_TEMP_TEXT = "Я ещё не открыл двери своего магазинчика 😉"
