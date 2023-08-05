from aiogram.utils.callback_data import CallbackData

YES_CB = CallbackData('yes', 'order_id', 'user_id', 'state')
NO_CB = CallbackData('no', 'order_id', 'user_id', 'state')

ORDER_STATE_CB = CallbackData('order_accepted', 'order_id', 'user_id', 'state')

ORDER_ISSUED_CB = CallbackData('order_issued', 'order_id', 'user_id')
