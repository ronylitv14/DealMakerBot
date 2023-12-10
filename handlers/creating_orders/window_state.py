from aiogram.filters.state import State, StatesGroup


class OrderState(StatesGroup):
    main = State()
    adding_subjects = State()
    creating_price = State()
    deadline = State()
    adding_description = State()

    adding_materials = State()
