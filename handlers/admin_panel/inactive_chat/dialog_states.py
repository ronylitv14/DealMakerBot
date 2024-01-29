from aiogram.fsm.state import State, StatesGroup


class InactiveChat(StatesGroup):
    query_chat = State()
    accept_action = State()