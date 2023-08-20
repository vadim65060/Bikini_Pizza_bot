from aiogram import types
from aiogram.dispatcher import FSMContext, filters
from aiogram.types import Message, CallbackQuery, ParseMode, ContentType, ShippingOption, LabeledPrice, ShippingQuery
from aiogram.utils.callback_data import CallbackData
from validator_collection import checkers

from bot_create import dp, config
from callbacks import menu_callbacks, order_callbacks
from create_db import data_base as db
from delivery import geocoder
from delivery.delivery_calculator import delivery_calculator
from fsm.menu_fsm import OrderState
from handlers.menu_handlers import send_menu_on_update
from markups import order_markups
from markups.menu_markups import menu_markup
from texts import order_texts
from handlers import order_escort_handlers

BUY_PAYLOAD = 'buy_payload'


async def back_check(message: Message, state: FSMContext):
    if message.text and message.text.casefold() == order_texts.BACK_TEXT.casefold():
        await send_menu_on_update(message, state)
        return True
    return False


async def back_to_menu(update: Message | CallbackQuery, state: FSMContext):
    if isinstance(update, CallbackQuery):
        await update.message.delete()
    await send_menu_on_update(update, state)


async def order_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Оформление заказа', reply_markup=order_markups.back_markup)
    await print_order(callback.message, state, callback.from_user.id)


async def select_pickup_address(callback: CallbackQuery):
    await callback.message.edit_text(order_texts.SELECT_SHOP_ADDRESSES_TEXT,
                                     reply_markup=order_markups.get_pickup_addresses(db))
    await OrderState.select_pickup_address.set()


async def set_pickup_address(callback: CallbackQuery, state: FSMContext, callback_data: dict):
    await state.update_data({'pickup_address': db.get_shop_address(int(callback_data['shop_id']))[0]})
    await print_order(callback, state, callback.from_user.id)


async def off_pickup(callback: CallbackQuery, state: FSMContext):
    await state.update_data({'pickup_address': None})
    await print_order(callback, state, callback.from_user.id)


async def select_balls_to_use(callback: CallbackQuery):
    await callback.message.edit_text(order_texts.BALLS_TEXT, reply_markup=None)
    await OrderState.balls_select.set()


async def set_balls_to_use(message: Message, state: FSMContext):
    price = db.get_order_sum(message.from_user.id)
    min_price = 1
    user_balance, = db.get_user_info(message.from_user.id, 'money')
    if not checkers.is_integer(message.text, minimum=0, maximum=max(min(user_balance, price - min_price), 0)):
        await message.answer(order_texts.INCORRECT_INPUT_NUM_TEXT.format(max(min(user_balance, price - min_price), 0)))
        return

    await state.update_data({'balls': int(message.text)})
    await OrderState.print_order.set()
    await print_order(message, state)


async def get_comment(callback: CallbackQuery):
    await callback.answer(order_texts.GET_COMMENT_TEXT)
    await OrderState.get_comment.set()


async def set_comment(message: Message, state: FSMContext):
    await state.update_data({'comment': message.text})
    await print_order(message, state)


async def buy(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    balls = data.get('balls')
    pickup_address = data.get('pickup_address')
    booked_list = db.booked_list(callback.from_user.id)
    prices = []
    for staff in booked_list:
        size_text = staff[4] if staff[4] is not None else ''
        prices.append(
            types.LabeledPrice(label=f'{staff[2]} {size_text} {staff[5]}шт.', amount=staff[3] * staff[5] * 100))
    if balls:
        prices.append(types.LabeledPrice(label=f'Баллы', amount=-balls * 100))
    await callback.bot.send_invoice(callback.message.chat.id,
                                    title='заказ в Bikini pizza',
                                    description=pickup_address if pickup_address else 'доставка',
                                    provider_token=config.provider_token,
                                    currency='rub',
                                    prices=prices,
                                    payload=BUY_PAYLOAD,
                                    need_phone_number=True,
                                    need_shipping_address=pickup_address is None,
                                    is_flexible=pickup_address is None,
                                    max_tip_amount=50000 * 100)


async def shipping_callback(query: ShippingQuery, state: FSMContext) -> None:
    if query.invoice_payload != BUY_PAYLOAD:
        await query.bot.answer_shipping_query(query.id, ok=False, error_message="Something went wrong...")
        return

    data = await state.get_data()
    balls = data.get('balls')
    price = db.get_order_sum(query.from_user.id) - (balls if balls else 0)
    shipping_address = query.shipping_address
    shipping_address_text = f'{shipping_address.city} {shipping_address.street_line1} {shipping_address.street_line2}'
    location = geocoder.coordinates(shipping_address_text)
    delivery_price, delivery_description = await delivery_calculator.get_delivery_price(location, price)
    print(delivery_price)
    print(delivery_description)
    if delivery_price is None:
        await query.bot.answer_shipping_query(query.id, ok=False, error_message=delivery_description)
        return

    options = list()
    options.append(ShippingOption('0', 'Доставка курьером', [LabeledPrice('Доставка', delivery_price * 100)]))
    await state.update_data({'delivery_cost': delivery_price})
    await query.bot.answer_shipping_query(query.id, ok=True, shipping_options=options)


@dp.pre_checkout_query_handler(lambda query: True, state='*')
async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery, state: FSMContext):
    if pre_checkout_q.invoice_payload != BUY_PAYLOAD:
        await pre_checkout_q.bot.answer_pre_checkout_query(pre_checkout_q.id, ok=False,
                                                           error_message="Something went wrong...")
        return
    data = await state.get_data()
    balls = data.get('balls')
    if balls:
        user_balance, = db.get_user_info(pre_checkout_q.from_user.id, 'money')
        if user_balance < balls:
            await pre_checkout_q.bot.answer_pre_checkout_query(pre_checkout_q.id, ok=False,
                                                               error_message='не хватает баллов на счету')
    stuff_ids = db.get_purchases_by_id(pre_checkout_q.from_user.id, 'stuff_id')
    ids = []
    for stuff_id in stuff_ids:
        ids.append(stuff_id[0])
    stuff_show = db.get_stuff_info_by_id_array(ids, 'id, show')
    delete_flag = False
    for stuff in stuff_show:
        if not stuff[1]:
            db.delete_user_purchase(pre_checkout_q.from_user.id, stuff[0])
            delete_flag = True

    if delete_flag:
        await pre_checkout_q.bot.answer_pre_checkout_query(pre_checkout_q.id, ok=False,
                                                           error_message='некоторые товары отсутствуют, '
                                                                         'оформите заказ заново')
        await pre_checkout_q.bot.delete_message(pre_checkout_q.from_user.id, pre_checkout_q.id)
    else:
        await pre_checkout_q.bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


async def successful_payment(message: Message, state: FSMContext):
    data = await state.get_data()
    payment = message.successful_payment
    phone = payment.order_info.phone_number
    shipping_address = payment.order_info.shipping_address
    if shipping_address:
        address = f'{shipping_address.city} {shipping_address.street_line1} {shipping_address.street_line2}'
    else:
        address = data.get('pickup_address') + ' (самовывоз)'
    balls = data.get('balls')
    delivery_cost = data.get('delivery_cost')
    if delivery_cost is None:
        delivery_cost = 0
    comment = data.get('comment')
    order_id = db.checkout(message.from_user.id, payment.total_amount // 100, balls, delivery_cost, phone, address,
                           comment, payment.telegram_payment_charge_id, payment.provider_payment_charge_id)
    await order_escort_handlers.print_order(order_id)
    await message.answer(
        order_texts.ORDER_COMPLETED_TEXT.format(order_id, payment.total_amount // 100, payment.currency),
        reply_markup=menu_markup)
    await state.finish()


async def print_order(update: Message | CallbackQuery, state: FSMContext, user_id=None):
    await OrderState.print_order.set()
    data = await state.get_data()
    pickup_address = data.get('pickup_address')
    balls = data.get('balls')
    comment = data.get('comment')
    if user_id is None:
        user_id = update.from_user.id
    text = order_texts.get_order_text(db, user_id, balls, pickup_address, comment)
    if isinstance(update, CallbackQuery):
        await update.message.edit_text(text, reply_markup=order_markups.get_order_markup(pickup_address),
                                       parse_mode=ParseMode.HTML)
    else:
        await update.answer(text, reply_markup=order_markups.get_order_markup(pickup_address),
                            parse_mode=ParseMode.HTML)


def register_order_handlers():
    dp.register_message_handler(back_to_menu, filters.Text(equals=order_texts.BACK_TEXT, ignore_case=True),
                                state=OrderState.all_states)
    dp.register_callback_query_handler(back_to_menu,
                                       CallbackData(order_callbacks.CANCEL_CB).filter(),
                                       state={OrderState.print_order, None})

    dp.register_callback_query_handler(order_start,
                                       CallbackData(menu_callbacks.ORDER_CB).filter(),
                                       state=None)

    dp.register_callback_query_handler(select_pickup_address,
                                       CallbackData(order_callbacks.PICKUP_CB).filter(),
                                       state=OrderState.print_order)
    dp.register_callback_query_handler(set_pickup_address,
                                       order_callbacks.SHOP_ADDRESSES_CB.filter(),
                                       state=OrderState.select_pickup_address)
    dp.register_callback_query_handler(off_pickup,
                                       CallbackData(order_callbacks.DELIVERY_CB).filter(),
                                       state=OrderState.print_order)
    dp.register_callback_query_handler(select_balls_to_use,
                                       CallbackData(order_callbacks.USE_BALL_CB).filter(),
                                       state=OrderState.print_order)
    dp.register_callback_query_handler(get_comment,
                                       CallbackData(order_callbacks.ADD_COMMENT_CB).filter(),
                                       state=OrderState.print_order)
    dp.register_message_handler(set_comment,
                                state=OrderState.get_comment)

    dp.register_message_handler(set_balls_to_use,
                                state=OrderState.balls_select)

    dp.register_callback_query_handler(buy,
                                       CallbackData(order_callbacks.ORDER_CB).filter(),
                                       state=OrderState.print_order)
    dp.register_shipping_query_handler(shipping_callback, state='*')
    dp.register_message_handler(successful_payment, content_types=ContentType.SUCCESSFUL_PAYMENT, state='*')
