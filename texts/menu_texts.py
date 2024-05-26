# Тексты кнопок
import constants
from database.db_funcs import DataBase

MENU_PROFILE_BUTTON_TEXT = "Корзина"
MENU_STORE_BUTTON_TEXT = "Магазин"
MENU_PROMO_BUTTON_TEXT = "Ввести промокод"
MENU_PROMOTIONS_BUTTON_TEXT = "Акции"
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

HELP_INPUT_REQUEST = "Введи свой вопрос"
HELP_MESSAGE_SENT = "Запрос отправлен, возвращаю тебя в меню"
BACK_TO_MENU_TEXT = "Хорошо, возвращаю тебя в меню"
TO_SUPPORT_MESSAGE_TEMPLATE = "Пользователь: @{}\n" \
                              "userid: <code>{}</code>\n" \
                              "Вопрос:\n{}"

PROMO_INPUT_REQUEST = "Если у тебя есть промокод, введи его сюда"
PROMO_SUCCESSFULLY_ACTIVATED_TEMPLATE = "Промокод на {} Bikini coins активирован! Возвращаю тебя в меню 😎"
PROMO_ALREADY_USED = "Ты уже вводил этот промокод, возвращаю тебя в меню"
PROMO_DOESNT_EXISTS = "Промокод недействителен 😕 Попробуй ещё раз!"

STORE_TEMP_TEXT = "Я ещё не открыл двери своего магазинчика 😉"

MENU_PROMOTIONS_TEXT = '''Наши акции на пиццу:
<B>2+1</B>. Заказываете у нас <B>2</B> большие пиццы <B>на вынос или в ресторане</B> и получаете третью большую бесплатно.
<B>3+1</B>. Заказываете у нас <B>3</B> большие пиццы <B>на доставку</B> и получаете четвёртую большую бесплатно.

* Подарочную пиццу определяем мы и раз в неделю меняем. Подробности у оператора или в наших соц. сетях.
** Пицца "Марго" не учавствует в акции, но мы всегда можем сделать ее вместо подарочной пиццы)'''

FAQ_TEXT = f'''• Что такое "коины"?
Коины - это наши бонусные баллы. За каждый ваш заказ мы возвращаем вам <B>{int(constants.CASHBACK_PERCENT * 100)}%</B> его стоимости обратно в виде этих самых коинов. Круто, правда? 😎

• Как начать зарабатывать "коины"?
Используйте код <code>bikini200</code> и получите <B>200 коинов</B>, в главном меню есть кнопка 😉
А ещё баллы будут капать за каждую вашу покупку. Чем больше заказов, тем больше коинов! 💪

• Как потратить накопленное?
Можно оплатить до <B>{int(constants.BALLS_USING_LIMIT_PERCENT * 100)}%</B> от вашей покупки коинами! Когда будете оформлять заказ, просто выберите опцию "<B>баллы</B>", укажите сколько хотите потратить, и вуаля! 🎉

• А на доставку и акции распространяется?
<B>Здесь важно</B>: коины <B>не</B> работают с акциями и на доставку 🚚

Если остались вопросы или нашли ошибку, пишите в поддержку 👇'''
