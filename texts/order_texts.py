from database.db_funcs import DataBase
from texts.menu_texts import get_profile_text

GET_PHONE_TEXT = "Введи номер телефона для связи"
WRONG_PHONE_TEXT = "Не корректный номер телефона, попробуйте снова"

GET_ADDRESS_TEXT = "Введи адрес для доставки или отправь геопозицию,\n" \
                   "для самовывоза нажми кнопку"

BACK_TEXT = 'назад'

PICKUP_TEXT = 'самовывоз'
DELIVERY_TEXT = 'доставка'
SELECT_SHOP_ADDRESSES_TEXT = "Выбери место самовывоза"
BALLS_TEXT = "Сколько баллов использовать? (напиши целое число)"
INCORRECT_INPUT_NUM_TEXT = "введи целое число от 0 до {}"
GET_COMMENT_TEXT = 'введи комментарий'

EDIT_PHONE_BUTTON_TEXT = 'изменить номер'
EDIT_ADDRESS_BUTTON_TEXT = 'изменить адресс'
ORDER_BUTTON_TEXT = 'заказать'
CANCEL_BUTTON_TEXT = 'отмена'
USE_BALLS_BUTTON_TEXT = 'баллы'
ADD_COMMENT_TEXT = 'комментарий'
DELIVERY_ZONE_BUTTON_TEXT = 'Зоны доставки'
DELIVERY_ZONE_URL = 'https://yandex.ru/maps/?um=constructor' \
                    '%3A38e7ac5af51607ab4e996b58fe775240204ebf377075397488c961da2eae134d&source=constructorLink'

ORDER_COMPLETED_TEXT = "Заказ №{} на сумму {} {} получен, ожидайте ответ."


def get_order_text(db: DataBase, tg_id: int, balls: int, pickup_address: str, comment: str | None):
    text, price = get_profile_text(db, tg_id, False)
    if balls:
        price = max(1, price - balls)
        text += f'Bikini coins - {balls}\n'

    text += f'---------------\n'
    text += f'Итого: {price}RUB\n'
    if pickup_address:
        text += f'\nСамовывоз: {pickup_address}'

    if comment:
        text += f'\nКомментарий: {comment}'

    return text
