from aiogram import F
from aiogram.filters import or_f, and_f
from aiogram.enums import ChatType
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.dispatcher.router import Router
from aiogram.fsm.context import FSMContext

from aiogram_dialog.api.entities import StartMode
from aiogram_dialog.dialog import DialogManager

from handlers.states_handler import ClientDialog, ExecutorDialog
from handlers.deals.dialog_windows import create_dialog_client
from handlers.deals.window_state import CreateDeal, DealsGroup

from handlers.deals_executor.dialog_states import DealsExecutor
from handlers.deals_executor.dialog_windows import create_dialog_deal_executor

from database.models import PropositionBy

deals_router = Router()

deals_router.include_routers(*create_dialog_client())
deals_router.include_routers(create_dialog_deal_executor())
deals_router.message.filter(F.chat.type.in_({ChatType.PRIVATE}))


@deals_router.message(
    F.text.contains("➕"),
    ClientDialog.client_state
)
async def get_deals_dialog_client(message: Message, state: FSMContext, dialog_manager: DialogManager):
    cur_state = await state.get_state()

    await message.answer(
        text="Перейдемо до огляду ваших угод",
        reply_markup=ReplyKeyboardRemove()
    )

    await dialog_manager.start(state=DealsGroup.main_deals, mode=StartMode.NORMAL)
    dialog_manager.dialog_data["cur_state"] = cur_state
    dialog_manager.dialog_data["state_obj"] = state
    dialog_manager.dialog_data["proposed_by"] = PropositionBy.executor


@deals_router.message(
    F.text.contains("➕"),
    ExecutorDialog.executor_state
)
async def get_deals_dialog_executor(message: Message, state: FSMContext, dialog_manager: DialogManager):
    cur_state = await state.get_state()

    await message.answer(
        text="Перейдемо до огляду ваших угод",
        reply_markup=ReplyKeyboardRemove()
    )

    await dialog_manager.start(state=DealsExecutor.query_user, mode=StartMode.NORMAL)
    dialog_manager.dialog_data["cur_state"] = cur_state
    dialog_manager.dialog_data["state_obj"] = state
    dialog_manager.dialog_data["proposed_by"] = PropositionBy.client
