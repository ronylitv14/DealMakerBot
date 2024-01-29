from aiogram.fsm.state import State, StatesGroup


class ReviewStates(StatesGroup):
    specify_rating = State()
    choose_positives = State()
    choose_negatives = State()
    add_comment = State()
