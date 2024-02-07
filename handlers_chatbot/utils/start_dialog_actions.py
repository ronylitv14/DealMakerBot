from database_api.components.chats import ChatsList, Chats
from aiogram.types import Message
from aiogram_dialog.dialog import DialogManager
from aiogram_dialog.api.entities import StartMode, ShowMode

from handlers_chatbot.switching_chat.dialog_states import SwitchingChatStates
from utils.redis_utils import deactivate_all_unused_sessions


async def start_get_chat_dialog(message: Message, dialog_manager: DialogManager, **kwargs):
    user_chats: ChatsList = await Chats().get_all_user_chats(client_id=message.from_user.id).do_request()

    if not isinstance(user_chats, ChatsList):
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
        show_mode=ShowMode.SEND,
        data={
            "chats": user_chats.model_dump(mode="json")
        }
    )
