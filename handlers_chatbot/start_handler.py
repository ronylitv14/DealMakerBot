from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.filters.command import Command, CommandStart, CommandObject
from aiogram.dispatcher.router import Router
from aiogram_dialog.dialog import DialogManager
from aiogram_dialog.api.entities import StartMode, ShowMode

from middlewares.close_dialog_mw import EndChatDialogMiddleware
from handlers_chatbot.chat_handler import chat_router
from handlers_chatbot.creating_chat.dialog_states import ChatState
from handlers_chatbot.creating_chat.dialog_windows import create_chatting_dialog
from handlers_chatbot.switching_chat.dialog_states import SwitchingChatStates
from handlers_chatbot.switching_chat.dialog_windows import create_switching_chat_dialog

from handlers_chatbot.paying_handler import paying_router
from handlers_chatbot.error_handler import error_router
from handlers_chatbot.utils.start_dialog_actions import start_get_chat_dialog
from utils.redis_utils import send_stored_messages
from database_api.components.chats import Chats, ChatModel

main_router = Router()
main_router.message.middleware(EndChatDialogMiddleware())
main_router.include_routers(paying_router, chat_router, error_router)
main_router.include_routers(create_chatting_dialog(), create_switching_chat_dialog())


@main_router.message(
    Command("get_chat")
)
async def get_all_chats(message: Message, dialog_manager: DialogManager, **kwargs):
    await start_get_chat_dialog(
        message=message,
        dialog_manager=dialog_manager,
        state=SwitchingChatStates.all_chats
    )


async def start_chat_action(dialog_manager: DialogManager, start_data: str = None, callback: CallbackQuery = None):
    if (start_data is None) and (callback is None):
        raise ValueError("Should specify one param")
    elif (start_data is not None) and (callback is not None):
        raise ValueError("Should only one param be specified")

    action, db_chat_id = callback.data.split("|") if callback else start_data.split("-")

    chat_obj: ChatModel = await Chats().get_chat_data(db_chat_id=int(db_chat_id)).do_request()

    if dialog_manager.event.from_user.id != chat_obj.client_id or chat_obj.active is False:
        return await dialog_manager.event.answer("Це не ваш чат як клієнта!")

    session_key = f"session:{chat_obj.client_id}:{chat_obj.id}"

    await dialog_manager.start(
        state=ChatState.chatting_state,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.EDIT,
        data={
            "chat_obj": chat_obj.model_dump(mode="json")
        },

    )

    await send_stored_messages(
        session_key,
        bot=dialog_manager.event.bot,
        chat_id=chat_obj.client_id
    )


@main_router.message(
    CommandStart()
)
async def handle_start_command(message: Message, command: CommandObject, dialog_manager: DialogManager):
    start_data = command.args

    if not start_data:
        return await message.answer("Неможливо розпочати чат! Помилка")

    await start_chat_action(
        dialog_manager=dialog_manager,
        start_data=start_data
    )


@main_router.callback_query(
    F.data.contains("chat-start")
)
async def handle_start_chatting(callback: CallbackQuery, dialog_manager: DialogManager):
    await start_chat_action(
        dialog_manager=dialog_manager,
        callback=callback
    )

    await callback.answer()
