from aiogram.fsm.state import State, StatesGroup


class ClientDialog(StatesGroup):
    client_state = State()
    creating_order = State()
    my_orders = State()
    checking_balance = State()
    profile = State()


class ProfileDialog(StatesGroup):
    edit_phone = State()
    edit_name = State()
    edit_password = State()
    edit_email = State()
    delete_account = State()


class ExecutorDialog(StatesGroup):
    executor_state = State()
    profile = State()
