from aiogram.filters import Command, CommandObject
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.dispatcher.router import Router
from aiogram_dialog.dialog import DialogManager

from handlers.orders_handler import order_router
from handlers.balance_handler import balance_router
from handlers.profile_handler import profile_router
from handlers.utils.start_action_handler import HandleAction, ACTIONS
from handlers.executor_profile_handler import executor_router
from handlers.deals_handler import deals_router
from handlers.send_client_msg.dialog_windows import msg_dialog
from handlers.admin_handler import admin_panel_router
from handlers.tickets_handler import ticket_router
from handlers.menu_handler import menu_router
from handlers.review_handler import review_router

from aiogram_dialog.api.exceptions import UnknownIntent, OutdatedIntent
from middlewares.auth_middelware import InnerAuthMiddleware
from middlewares.rate_limits import RateLimitMiddleware
from middlewares.close_dialog_mw import CloseDialogMiddleware

main_router = Router()
main_router.include_routers(
    order_router,
    balance_router,
    profile_router,
    executor_router,
    deals_router,
    admin_panel_router,
    msg_dialog,
    ticket_router,
    menu_router,
    review_router
)
main_router.message.middleware(InnerAuthMiddleware())
main_router.message.middleware(CloseDialogMiddleware())
main_router.callback_query.middleware(RateLimitMiddleware())


@main_router.error()
async def handle_outdated_intent(event: types.ErrorEvent):
    if isinstance(event.exception, UnknownIntent) or isinstance(event.exception, OutdatedIntent):
        return await event.update.callback_query.answer("Вибачте, зараз не можливо виконати такий запит!")
    raise event.exception


@main_router.message(Command('start'))
async def start_command_handler(message: types.Message, command: CommandObject, state: FSMContext,
                                dialog_manager: DialogManager):
    try:
        task_id, action = command.args.split("-")
        task_id = int(task_id)

        if action not in ACTIONS:
            raise ValueError

        action_handler = HandleAction(
            action=action,
            task_id=task_id,
            message=message,
            manager=dialog_manager,
            state=state
        )
        processor = await action_handler.choose_action()
        await processor.process_action()
    except (ValueError, AttributeError):
        await message.answer(
            text="Вітаємо вас у нашому боті!"
        )
