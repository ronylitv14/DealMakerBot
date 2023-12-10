from aiogram_dialog.dialog import Dialog, DialogManager
from aiogram_dialog.window import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.text import Format
from aiogram_dialog.api.entities import ShowMode
from aiogram.fsm.state import State, StatesGroup
from aiogram.enums import ContentType
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton


class SendMessageClient(StatesGroup):
    main = State()


async def send_message_to_client(message: Message, widget: MessageInput, manager: DialogManager):
    chat_id = manager.start_data.get("client_chat_id")
    executor_id = manager.start_data.get("executor_tg_id")
    task_id = manager.start_data.get("task_id")
    executor_username = manager.start_data.get("username")

    manager.show_mode = ShowMode.EDIT
    await message.bot.send_message(
        chat_id=chat_id,
        text="Ваше замовлення хочуть взяти! Для створення з цим замовником чату натисніть на кнопку нижче."
             f"Його повідомлення: \n\n<b><i>{message.text}</i></b>",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Створити чат",
                        callback_data=f"create-chat|{chat_id}|{executor_id}|{task_id}|{executor_username}"
                    )
                ]
            ]
        ),
        parse_mode="HTML"
    )
    await message.answer(
        text="<b>Ваше повідомлення відправлене клієнту!</b>",
        parse_mode="HTML"
    )
    await manager.done()


msg_input = MessageInput(
    func=send_message_to_client,
    content_types=ContentType.TEXT

)

main_window = Window(
    Format("Напишуть будь ласка повідомлення для клієнта, щоб він обрав саме вас!"),
    msg_input,
    state=SendMessageClient.main
)

msg_dialog = Dialog(
    main_window
)
