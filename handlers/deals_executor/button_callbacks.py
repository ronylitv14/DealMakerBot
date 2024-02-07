from aiogram.types import Message
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.dialog import DialogManager

from database_api.components.users import Users, UserResponseList


class InputCallbacks:
    @staticmethod
    async def get_all_possible_users(message: Message, widget: MessageInput, manager: DialogManager):
        users = await Users().get_similar_users(name=message.text).do_request()
        if not isinstance(users, UserResponseList):
            return await message.answer("Спробуйте ще раз! Таких користувачів не знайдено!")

        manager.dialog_data["users"] = users.model_dump(mode="json")

        await manager.next()
