from pprint import pprint

from aiogram import F
from aiogram.filters import or_f
from aiogram.types import Message, ContentType, CallbackQuery
from aiogram.filters.command import Command, CommandStart, CommandObject
from aiogram.dispatcher.router import Router
from aiogram_dialog.dialog import DialogManager
from aiogram_dialog.api.entities import StartMode, ShowMode

from handlers_chatbot.chat_handler import chat_router
from handlers_chatbot.creating_chat.dialog_states import ChatState
from handlers_chatbot.creating_chat.dialog_windows import create_chatting_dialog
from handlers_chatbot.switching_chat.dialog_states import SwitchingChatStates
from handlers_chatbot.switching_chat.dialog_windows import create_switching_chat_dialog

from handlers_chatbot.utils.redis_interaction import activate_session, send_stored_messages, \
    deactivate_all_unused_sessions
from handlers_chatbot.paying_handler import paying_router

from database.crud import get_chat_object, get_all_user_chats

main_router = Router()
main_router.include_routers(paying_router, chat_router)
main_router.include_routers(create_chatting_dialog(), create_switching_chat_dialog())


@main_router.message(
    Command("get_chat")
)
async def get_all_chats(message: Message, dialog_manager: DialogManager, **kwargs):
    user_chats = await get_all_user_chats(message.from_user.id)

    if not user_chats:
        return await message.answer(
            text="<b>У вас немає чатів у якості клієнта!</b>",
            parse_mode="HTML"
        )

    await deactivate_all_unused_sessions(
        session_key="all",
        client_id=message.from_user.id
    )

    await dialog_manager.start(
        state=SwitchingChatStates.all_chats,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.EDIT,
        data={
            "chats": user_chats
        }
    )


async def start_chat_action(dialog_manager: DialogManager, start_data: str = None, callback: CallbackQuery = None):
    if (start_data is None) and (callback is None):
        raise ValueError("Should specify one param")
    elif (start_data is not None) and (callback is not None):
        raise ValueError("Should only one param be specified")

    action, db_chat_id = callback.data.split("|") if callback else start_data.split("-")

    chat_obj = await get_chat_object(
        db_chat_id=int(db_chat_id)
    )

    session_key = f"session:{chat_obj.client_id}:{chat_obj.id}"

    await dialog_manager.start(
        state=ChatState.chatting_state,
        mode=StartMode.NORMAL,
        show_mode=ShowMode.EDIT,
        data={
            "chat_obj": chat_obj
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
        return await message.answer("Неможливо розпочати чат! Помилкка")

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
