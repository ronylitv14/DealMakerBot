from aiogram_dialog.dialog import Dialog, DialogManager
from aiogram_dialog.window import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.text import Format
from aiogram_dialog.widgets.kbd import Cancel
from aiogram_dialog.api.entities import ShowMode
from aiogram.fsm.state import State, StatesGroup
from aiogram.enums import ContentType
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from database_api.components.reviews import Reviews, UserReviewResponse
from telegraph_pages.executor_profile import get_summary_url, create_executor_summary_text


class SendMessageClient(StatesGroup):
    main = State()


async def send_message_to_client(message: Message, widget: MessageInput, manager: DialogManager):
    chat_id = manager.start_data.get("client_chat_id")
    executor_id = manager.start_data.get("executor_tg_id")
    task_id = manager.start_data.get("task_id")
    executor_username = manager.start_data.get("username")

    print(executor_id)

    summary_text = ""

    executor_reviews: UserReviewResponse = await Reviews().get_user_reviews(executor_id).do_request()

    if isinstance(executor_reviews, UserReviewResponse):
        url = await get_summary_url(
            reviews=executor_reviews
        )
        summary_text = create_executor_summary_text(url)

    manager.show_mode = ShowMode.EDIT
    await message.bot.send_message(
        chat_id=chat_id,
        text=f"{summary_text}"
             "Ваше замовлення хочуть взяти! Для створення з цим замовником чату натисніть на кнопку нижче. "
             f"Його повідомлення: \n\n<b>{message.text}</b>",
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
    Cancel(Format("Відмінити")),
    state=SendMessageClient.main
)

msg_dialog = Dialog(
    main_window
)
