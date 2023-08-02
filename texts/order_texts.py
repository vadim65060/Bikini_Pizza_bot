from database.db_funcs import DataBase
from texts.menu_texts import get_profile_text

GET_PHONE_TEXT = "Введи номер телефона для связи"
WRONG_PHONE_TEXT = "Не корректный номер телефона, попробуйте снова"

GET_ADDRESS_TEXT = "Введи адрес для доставки или отправь геопозицию,\n" \
                   "для самовывоза нажми кнопку"

BACK_TEXT = 'назад'

PICKUP_TEXT = 'самовывоз'
SELECT_SHOP_ADDRESSES_TEXT = "Выбери место самовывоза"
BALLS_TEXT = "Сколько баллов использовать? (напиши целое число)"
INCORRECT_INPUT_NUM_TEXT = "введи целое число от 0 до {}"

EDIT_PHONE_BUTTON_TEXT = 'изменить номер'
EDIT_ADDRESS_BUTTON_TEXT = 'изменить адресс'
ORDER_BUTTON_TEXT = 'заказать'
CANCEL_BUTTON_TEXT = 'отмена'
USE_BALLS_BUTTON_TEXT = 'использовать баллы'
DELIVERY_ZONE_BUTTON_TEXT = 'Зоны доставки'
DELIVERY_ZONE_URL = 'https://yandex.ru/maps/?um=constructor' \
                    '%3A38e7ac5af51607ab4e996b58fe775240204ebf377075397488c961da2eae134d&source=constructorLink'

ORDER_COMPLETED_TEXT = "Заказ на сумму {} {} принят, приятного аппетита!"


def get_order_text(db: DataBase, tg_id: int, phone: str, delivery, balls: int = None, address: str = None,
                   pickup=False):
    delivery_none = False
    text, price = get_profile_text(db, tg_id)
    if delivery[0] is None and not pickup:
        text += '\n' + delivery[1]
        delivery_none = True
    if not pickup and delivery[0] and delivery[0] > 0:
        price += delivery[0]
        text += f'доставка - {delivery[0]}RUB\n'
    if not delivery_none:
        text += f'---------------\n' \
                f'Сумма: {price}RUB'
        if balls:
            price = max(1, price - balls)
            text += f'\nиспользованные баллы - {balls}\n' \
                    f'Итого: {price}RUB'
        text += f'\n\nномер: {phone}'
    if address is not None:
        text += f'\nадрес: {address}'
        if pickup:
            text += ' (самовывоз)'
    return text
