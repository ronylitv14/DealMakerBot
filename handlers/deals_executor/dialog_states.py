from aiogram.fsm.state import State, StatesGroup


class DealsExecutor(StatesGroup):
    query_user = State()
    choose_user = State()
