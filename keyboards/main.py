from aiogram.types import ReplyKeyboardRemove
from aiogram_dialog import DialogManager

from handlers.states_handler import ClientDialog, ExecutorDialog
from keyboards.clients import create_keyboard_client
from keyboards.executors import create_keyboard_executor


async def create_keyboard_by_state(cur_state, dialog_manager: DialogManager):
    if cur_state == ClientDialog.client_state:
        await dialog_manager.event.answer(
            text="Обери наступну дію",
            reply_markup=create_keyboard_client(),
            parse_mode="HTML"
        )
    elif cur_state == ExecutorDialog.executor_state:
        await dialog_manager.event.answer(
            text="Обери наступну дію",
            reply_markup=create_keyboard_executor(),
            parse_mode="HTML"
        )
    else:
        await dialog_manager.event.answer(
            text="Натискай /menu для продовження роботи!",
            reply_markup=ReplyKeyboardRemove()
        )
