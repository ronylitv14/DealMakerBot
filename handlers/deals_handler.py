from aiogram import F
from aiogram.filters import or_f
from aiogram.enums import ChatType
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.dispatcher.router import Router
from aiogram.fsm.context import FSMContext

from aiogram_dialog.api.entities import StartMode
from aiogram_dialog.dialog import DialogManager

from handlers.states_handler import ClientDialog, ExecutorDialog
from handlers.deals.dialog_windows import create_dialog_client
from handlers.deals.window_state import DealsGroup
from handlers.deals_executor.dialog_windows import create_dialog_deal_executor
from utils.dialog_texts import get_deals_warning

from database_api.components.tasks import PropositionBy


deals_router = Router()

deals_router.include_routers(*create_dialog_client())
deals_router.include_routers(create_dialog_deal_executor())
deals_router.message.filter(F.chat.type.in_({ChatType.PRIVATE}))


@deals_router.message(
    F.text.contains("➕"),
    or_f(ClientDialog.client_state, ExecutorDialog.executor_state)
)
async def get_user_deals(message: Message, state: FSMContext, dialog_manager: DialogManager):
    cur_state = await state.get_state()

    await message.answer(
        text="Перейдемо до огляду ваших угод",
        reply_markup=ReplyKeyboardRemove()
    )
    await message.reply(
        text=get_deals_warning("клієнта" if cur_state == ClientDialog.client_state else "виконавця"),
        parse_mode="HTML"
    )

    await dialog_manager.start(state=DealsGroup.main_deals, mode=StartMode.RESET_STACK)
    dialog_manager.dialog_data["cur_state"] = cur_state
    dialog_manager.dialog_data["state_obj"] = state
    dialog_manager.dialog_data["proposed_by"] = PropositionBy.client if cur_state == ClientDialog.client_state\
        else PropositionBy.executor

    dialog_manager.dialog_data["proposed_for"] = PropositionBy.executor if cur_state == ClientDialog.client_state\
        else PropositionBy.client

