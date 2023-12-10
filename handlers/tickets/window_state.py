from aiogram.fsm.state import State, StatesGroup


class Tickets(StatesGroup):
    add_subject = State()
    add_description = State()
