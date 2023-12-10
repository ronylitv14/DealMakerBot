from aiogram.types import Message
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.dialog import DialogManager

from database.crud import get_similarity_users


class InputCallbacks:
    @staticmethod
    async def get_all_possible_users(message: Message, widget: MessageInput, manager: DialogManager):
        users = await get_similarity_users(name=message.text)

        manager.dialog_data["users"] = users

        await manager.next()
