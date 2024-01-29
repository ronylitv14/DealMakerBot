from aiogram.fsm.state import State, StatesGroup


class DealsGroup(StatesGroup):
    main_deals = State()
    watch_deals = State()


class CreateDeal(StatesGroup):
    choose_nickname = State()
    add_description = State()
    add_task_type = State()
    add_subject = State()
    add_price = State()
    add_files = State()
