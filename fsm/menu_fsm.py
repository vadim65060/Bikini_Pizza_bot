from aiogram.dispatcher.filters.state import StatesGroup, State


class SupportState(StatesGroup):
    input_wait = State()


class PromoState(StatesGroup):
    input_wait = State()


class LetteringState(StatesGroup):
    get_text = State()
    lettering_confirmation = State()


class OrderState(StatesGroup):
    get_comment = State()
    get_address = State()
    select_pickup_address = State()
    balls_select = State()
    print_order = State()
