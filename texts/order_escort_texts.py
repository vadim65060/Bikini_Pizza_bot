ORDER_ACCEPTED_BUTTON_TEXT = 'заказ принят'
ORDER_ACCEPTED_USER_TEXT = 'Ваш заказ принят!'

ORDER_COOKING_BUTTON_TEXT = 'заказ готовится'
ORDER_COOKING_USER_TEXT = 'Приступаем к готовке'

ORDER_DONE_BUTTON_TEXT = 'заказ готов'
ORDER_DONE_USER_TEXT = 'Ваш заказ приготовлен'

ORDER_DELIVERY_BUTTON_TEXT = 'заказ отправлен'
ORDER_DELIVERY_USER_TEXT = 'Ваш заказ отправлен'

ORDER_ISSUED_BUTTON_TEXT = 'заказ выдан'
ORDER_ISSUED_USER_TEXT = 'Приятного аппетита!'

ORDER_DELIVERED_BUTTON_TEXT = 'Заказ доставлен'
ORDER_DELIVERED_USER_TEXT = 'Ваш заказ доставлен!\nПриятного аппетита!'


def get_profile_text(order_id, purchases, order_info, username):
    total_price = 0
    coins = order_info[2]
    if order_info[2] is None:
        coins = 0
    text = f'Заказ №{order_id}\n\n'
    text += 'Состав:\n'
    for stuff_id, stuff_sizes_id, name, price, size, count in purchases:
        text += f"{name}"
        if size:
            text += f" {size}"
        text += f" {count}шт - {price * count}RUB\n"
        total_price += price * count
    text += f'Доставка - {order_info[3]}RUB\n'
    if order_info[1] - total_price - coins > 0:
        text += f'Чаевые - {order_info[1] - total_price - coins}RUB\n'
    text += f'Bikini coins - {coins}\n'
    text += f'---------------\n' \
            f'Итого: {order_info[1]}\n\n'
    text += 'Телефон: '
    if order_info[4][0] != '+' and order_info[4][0] != '8':
        text += '+'
    text += order_info[4] + '\n'
    if username and username != 'None':
        text += f'Телеграм: @{username}\n'
    text += f'Адрес: {order_info[5]}\n\n'
    if order_info[6] and order_info[6] != 'None':
        text += f'Комментарий: {order_info[6]}'

    return text
