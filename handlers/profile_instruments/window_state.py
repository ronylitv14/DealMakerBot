from aiogram.fsm.state import State, StatesGroup


class EditPhone(StatesGroup):
    auth_user = State()
    edit_object = State()
    accept_change = State()


class EditNickName(StatesGroup):
    auth_user = State()
    edit_object = State()
    accept_change = State()


class EditMail(StatesGroup):
    auth_user = State()
    edit_object = State()
    accept_change = State()


class DeleteAccount(StatesGroup):
    auth_user = State()
    accept_change = State()
