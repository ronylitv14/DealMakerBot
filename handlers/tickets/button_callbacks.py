from aiogram.types import Message
from aiogram_dialog.dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput

from database.crud import create_user_ticket


class ButtonCallbacks:
    @staticmethod
    async def process_description(message: Message, widget: MessageInput, manager: DialogManager):
        description = message.text

        await create_user_ticket(
            user_id=message.from_user.id,
            description=description,
            subject=manager.dialog_data.get("subject")
        )

        await message.answer(
            text="Ваш тікет успішно відправлено! Вам нададуть відповідь найближчим часом!"
        )

        await manager.done()
