from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.dialog import DialogManager
from aiogram.types import Message
from aiogram.enums import ContentType

from database_api.components.users import UserResponse
from database_api.components.warnings_component import Warnings


async def process_user_warning(message: Message, widget: MessageInput, manager: DialogManager):
    user: UserResponse = manager.start_data.get("user")
    warning = message.text

    await Warnings().save_warning_data(
        user_id=user.telegram_id,
        reason=warning,
        issued_by=message.from_user.id,
        warning_count=user.warning_count
    ).do_request()

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
