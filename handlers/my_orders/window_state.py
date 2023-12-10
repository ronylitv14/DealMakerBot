from aiogram.filters.state import State, StatesGroup


class MyOrders(StatesGroup):
    main = State()

    watch_orders = State()
