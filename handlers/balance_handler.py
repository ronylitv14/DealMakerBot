from typing import Any, Dict

from aiogram.dispatcher.router import Router
from aiogram import types, F
from aiogram.enums import ChatType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State

from aiogram_dialog.dialog import Dialog, DialogManager
from aiogram_dialog.api.entities import StartMode

from handlers.states_handler import ClientDialog
from .balance.window_state import BalanceGroup
from handlers.balance.dialog_windows import create_balance_dialogs

from database.crud import get_user_balance
from database.models import Balance

balance_router = Router()
balance_router.message.filter(F.chat.type.in_({ChatType.PRIVATE}))
balance_router.include_routers(*create_balance_dialogs())


@balance_router.message(
    F.text.contains("💵")
)
async def run_balance_dialog(message: types.Message, state: FSMContext, dialog_manager: DialogManager):

    balance: Balance = await get_user_balance(user_id=message.from_user.id)

    await message.answer(
        text="Переходимо до роботи з вашими коштами",
        reply_markup=types.ReplyKeyboardRemove()
    )
    cur_state = await state.get_state()
    await dialog_manager.start(
        BalanceGroup.main_window,
        mode=StartMode.RESET_STACK,
        data={
            "balance": balance.balance_money
        }
    )
    dialog_manager.dialog_data["state_object"] = state
    dialog_manager.dialog_data["cur_state"] = cur_state
