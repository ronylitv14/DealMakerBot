from aiogram.fsm.state import State, StatesGroup


class PriceOffer(StatesGroup):
    offer_price = State()


class PriceOfferAccept(StatesGroup):
    accept_price = State()
