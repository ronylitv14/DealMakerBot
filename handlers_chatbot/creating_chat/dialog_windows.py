from typing import Any

from aiogram_dialog.dialog import Dialog, DialogManager
from aiogram_dialog.window import Window
from aiogram_dialog.widgets.text import Format

from handlers_chatbot.creating_chat.dialog_states import ChatState
from handlers_chatbot.creating_chat.dialog_widgets import input_message, btn_end_chat

from utils.redis_utils import deactivate_session, is_session_active, activate_session

from database_api.components.chats import ChatModel


async def on_chat_dialog_start(data: Any, dialog_manager: DialogManager):
    # TODO: Add sessions deactivation

    chat_obj = dialog_manager.start_data.get("chat_obj")
    session_key = f"session:{chat_obj['client_id']}:{chat_obj['id']}"

    print(f"From func on_chat_dialog_start: {session_key}")
    await activate_session(session_key)


async def on_chat_dialog_close(data: Any, dialog_manager: DialogManager, *args, **kwargs):
    chat_obj = dialog_manager.start_data.get("chat_obj")
    session_key = f"session:{chat_obj['client_id']}:{chat_obj['id']}"
    is_active = await is_session_active(session_key)
    if is_active:
        await deactivate_session(session_key)
        print(f"From func on_chat_dialog_close: {session_key}")
        return


chatting_window = Window(
    Format("Ви розпочали чат щодо {start_data[chat_obj][group_name]}"),
    input_message,
    btn_end_chat,
    state=ChatState.chatting_state
)


def create_chatting_dialog():
    return Dialog(
        chatting_window,
        on_start=on_chat_dialog_start,
        on_close=on_chat_dialog_close
    )
