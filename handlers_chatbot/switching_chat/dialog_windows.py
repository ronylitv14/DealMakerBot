from aiogram_dialog.dialog import Dialog, DialogManager
from aiogram_dialog.window import Window
from aiogram_dialog.widgets.text import Const
from aiogram_dialog.widgets.kbd import Cancel

from handlers_chatbot.switching_chat.dialog_states import SwitchingChatStates
from handlers_chatbot.switching_chat.dialog_widgets import select_chat


async def chats_getter(**kwargs):
    manager: DialogManager = kwargs.get("dialog_manager")
    chats = manager.start_data.get("chats")

    preprocessed_chat_btns = []

    for ind, chat in enumerate(chats):
        preprocessed_chat_btns.append((chat, ind))

    return {
        "chats": preprocessed_chat_btns
    }


all_chats_window = Window(
    Const("Оберіть чат для початку діалогу!"),
    select_chat,
    Cancel(Const("Вийти")),
    state=SwitchingChatStates.all_chats,
    getter=chats_getter
)


def create_switching_chat_dialog():
    return Dialog(
        all_chats_window,
    )
