import abc
from aiogram import Bot
from aiogram.filters.command import CommandObject
from aiogram_dialog.widgets.text import Const, Format
from aiogram.enums import ContentType, ChatType
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.dialog import DialogManager
from aiogram.types import Message, CallbackQuery

from aiogram_dialog.api.entities import ShowMode
from handlers_chatbot.utils.redis_interaction import deactivate_session
from handlers_chatbot.utils.input_message import ChooseMessageHandler

from database.models import Chat


async def process_user_message(message: Message, widget: MessageInput, manager: DialogManager):
    if message.text:
        if message.text.startswith("/"):
            return await message.answer(
                text="<b>Не можна використовувати команди в режимі діалогу!</b>",
                parse_mode="HTML"
            )

    content_type = message.content_type
    chat_obj: Chat = manager.start_data.get("chat_obj")

    manager.show_mode = ShowMode.EDIT

    handler = ChooseMessageHandler(content_type=content_type).choose()
    if chat_obj.chat_type == ChatType.SUPERGROUP:
        return await handler(message=message, bot=message.bot).handle_message(chat_obj.supergroup_id)
    await handler(message=message, bot=message.bot).handle_message(-chat_obj.chat_id)


async def end_chat(callback: CallbackQuery, btn: Button, manager: DialogManager):
    chat_obj: Chat = manager.start_data.get("chat_obj")

    await manager.done()
    await callback.message.answer(
        text=f"Ви вийшли з чату: {chat_obj.group_name}"
    )
    await deactivate_session(
        session_key=f"session:{chat_obj.client_id}"
    )


input_message = MessageInput(
    func=process_user_message,
    content_types=ContentType.ANY
)

btn_end_chat = Button(Const("Вийти з чату"), id="btn_end", on_click=end_chat)
