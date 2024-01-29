from aiogram.types import Message
from aiogram_dialog.dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput

from database_api.components.tickets import Tickets


class ButtonCallbacks:
    @staticmethod
    async def process_description(message: Message, widget: MessageInput, manager: DialogManager):
        description = message.text

        await Tickets().save_ticket_data(
            user_id=message.from_user.id,
            description=description,
            subject=manager.dialog_data.get("subject")
        ).do_request()

        await message.answer(
            text="Ваш тікет успішно відправлено! Вам нададуть відповідь найближчим часом!"
        )

        await manager.done()
