from aiogram.fsm.state import State, StatesGroup


class CreatingProfile(StatesGroup):

    adding_description = State()
    adding_subjects = State()
    adding_task_examples = State()

    accept_all = State()
