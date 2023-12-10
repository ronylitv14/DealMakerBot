from aiogram.fsm.state import State, StatesGroup


class AuthStates(StatesGroup):
    get_username = State()
    get_email = State()

    get_password = State()
    repeat_password = State()
