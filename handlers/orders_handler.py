from uuid import uuid1

from aiogram import types, F
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext
from aiogram.dispatcher.router import Router

from aiogram_dialog import (
    DialogManager, StartMode, ShowMode
)
from aiogram.exceptions import TelegramBadRequest
from aiogram.enums import ChatType
from handlers.states_handler import ClientDialog, ExecutorDialog

from database_api.components.executors import Executors, ExecutorModel
from database_api.components.users import UserType

from utils.dialog_categories import subject_titles
from handlers.creating_orders.window_state import OrderState
from handlers.my_orders.window_state import MyOrders
from handlers.creating_orders.dialog_windows import create_orders_dialog
from handlers.my_orders.dialog_windows import create_my_orders_dialog

order_router = Router()
order_router.message.filter(F.chat.type.in_({ChatType.PRIVATE}))
order_router.include_routers(create_my_orders_dialog(), create_orders_dialog())


@order_router.message(
    F.text.contains("📝"),
    ClientDialog.client_state
)
async def create_order(message: types.Message, dialog_manager: DialogManager, state: FSMContext):
    await message.answer(
        text="Тепер перейдемо до створення вашого замовлення",
        reply_markup=types.ReplyKeyboardRemove()
    )
    cur_state = await state.get_state()

    await dialog_manager.start(OrderState.main, mode=StartMode.RESET_STACK)
    dialog_manager.dialog_data["subject_title"] = []
    # dialog_manager.dialog_data["state_obj"] = state
    dialog_manager.dialog_data["cur_state"] = cur_state
    dialog_manager.dialog_data["unique_id"] = str(uuid1())


@order_router.message(
    F.text.contains("📄"),
    or_f(ClientDialog.client_state, ExecutorDialog.executor_state)
)
async def get_my_orders(message: types.Message, state: FSMContext, dialog_manager: DialogManager):
    user_id = message.from_user.id
    cur_state = await state.get_state()

    executor = None

    if cur_state == ExecutorDialog.executor_state:
        executor = await Executors().get_executor_data(user_id).do_request()

    await message.answer(
        text="Переходимо до огляду замовлень",
        reply_markup=types.ReplyKeyboardRemove()
    )

    await dialog_manager.start(MyOrders.main, mode=StartMode.RESET_STACK, show_mode=ShowMode.SEND)

    dialog_manager.dialog_data["cur_state"] = cur_state
    dialog_manager.dialog_data["user_type"] = UserType.executor if executor else UserType.client
    dialog_manager.dialog_data["executor"] = executor.model_dump(mode="json") if isinstance(executor,
                                                                                            ExecutorModel) else None


@order_router.inline_query()
async def inline_query_handler(inline_query: types.InlineQuery, state: FSMContext):
    input_subject = inline_query.query
    cur_state = await state.get_state()

    if cur_state == ClientDialog.client_state and input_subject:
        results = []
        # FIXME: Create more accurate code for comparing queries

        for ind, subject in enumerate(subject_titles):
            if input_subject.lower() in subject.lower():
                results.append(types.InlineQueryResultArticle(
                    id=str(ind),
                    hide_url=True,
                    input_message_content=types.InputTextMessageContent(message_text=f"{subject}"),
                    title=f"{subject}"
                ))
        try:
            await inline_query.answer(
                results=results,
                is_personal=True
            )

        except TelegramBadRequest as err:
            print(err)
