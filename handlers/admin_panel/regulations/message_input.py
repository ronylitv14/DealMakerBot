from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.dialog import DialogManager
from aiogram.types import Message
from aiogram.enums import ContentType

from database.crud import create_user_warning
from database.models import User


async def process_user_warning(message: Message, widget: MessageInput, manager: DialogManager):
    user: User = manager.start_data.get("user")
    warning = message.text

    await create_user_warning(
        user_id=user.telegram_id,
        reason=warning,
        admin_id=message.from_user.id,
        warning_count=user.warning_count
    )

    await message.bot.send_message(
        chat_id=user.telegram_id,
        text="Вам було видано попередження!\n\n"
             f"Причина видачі: <i>{warning}</i>",
        parse_mode="HTML"
    )


input_warning = MessageInput(
    func=process_user_warning,
    content_types=ContentType.TEXT
)
