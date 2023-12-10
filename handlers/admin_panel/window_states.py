from aiogram.fsm.state import State, StatesGroup


class AdminPanel(StatesGroup):
    main_panel = State()


class WatchExecutorApplication(StatesGroup):
    watch_applications = State()
    review_application = State()


class WatchTickets(StatesGroup):
    watch_applications = State()
    review_application = State()


class WatchMoneyRetrieval(StatesGroup):
    watch_applications = State()
    review_application = State()
    add_invoice_id = State()


class UserData(StatesGroup):
    all_users = State()
    single_user = State()


class ChangeUserBalance(StatesGroup):
    change_balance = State()
    accept_new_balance = State()


class BanUser(StatesGroup):
    main_window = State()
    add_warning = State()
