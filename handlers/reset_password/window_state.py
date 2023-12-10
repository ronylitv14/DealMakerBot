from aiogram.fsm.state import State, StatesGroup


class EditPassword(StatesGroup):
    choose_option = State()
    check_random_token = State()
    reset_password = State()
    repeat_password = State()
