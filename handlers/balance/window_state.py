from aiogram.fsm.state import State, StatesGroup


class BalanceGroup(StatesGroup):
    main_window = State()

    adding_money = State()
    accept_request = State()


class WithdrawingMoneySub(StatesGroup):
    checking_password = State()
    withdraw_sum = State()
    # adding_cards = State()
    handle_cards = State()
    accept_withdraw = State()
