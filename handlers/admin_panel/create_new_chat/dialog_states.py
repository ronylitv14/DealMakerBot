from aiogram.fsm.state import State, StatesGroup


class CreatingCustomChat(StatesGroup):
    query_executor = State()
    select_exec = State()
    query_client = State()
    select_client = State()
    add_subject = State()
    add_description = State()
    accept_all = State()
