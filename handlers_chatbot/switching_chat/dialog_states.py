from aiogram.fsm.state import State, StatesGroup


class SwitchingChatStates(StatesGroup):
    all_chats = State()
