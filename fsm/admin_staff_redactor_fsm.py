from aiogram.dispatcher.filters.state import StatesGroup, State


class StuffCreateState(StatesGroup):
    set_name = State()
    set_price = State()
    set_category = State()
    set_description = State()
    set_count = State()
    set_image = State()
    set_show = State()


class StuffEditState(StatesGroup):
    select_stuff_category = State()
    select_stuff = State()
    select_field = State()
    edit_field_name = State()
    edit_field_price = State()
    edit_field_category = State()
    edit_field_description = State()
    edit_field_count = State()
    edit_field_image = State()
    edit_field_show = State()
    edit_size = State()
    edit_size_price = State()


class StuffDeleteState(StatesGroup):
    select_stuff_category = State()
    select_stuff = State()
    delete_stuff = State()


class CategoryCreateState(StatesGroup):
    set_name = State()
    set_description = State()
    set_image = State()


class CategoryEditState(StatesGroup):
    select_category = State()
    select_field = State()
    edit_name = State()
    edit_description = State()
    edit_image = State()


class CategoryDeleteState(StatesGroup):
    select_category = State()
    delete_stuff = State()
