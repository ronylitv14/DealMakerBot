import decimal
import os
from typing import Tuple

from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from telethon import Button
from telethon.types import ReplyInlineMarkup, KeyboardButtonRow
from dotenv import load_dotenv

from database_api.components.chats import ChatsList
from database_api.components.users import UserType

load_dotenv()

BOT_URL = os.getenv("BOT_URL")
CHAT_BOT_URL = os.getenv("CHAT_BOT_URL")


class CallbackConstructorReview:
    def __init__(self, reviewer_id: int, reviewed_id: int, task_id: int):
        self.reviewer_id = reviewer_id
        self.reviewed_id = reviewed_id
        self.task_id = task_id

    def construct_callback_data(self):
        return f"|{self.reviewer_id}|{self.reviewed_id}|{self.task_id}"

    @staticmethod
    def split_callback_data(callback_data: str) -> Tuple[int, int, int]:
        """
        Splits the callback data into its constituent parts.

        :param callback_data: The callback data string.
        :return: A tuple containing:
                 - reviewer_id (int): The reviewer's ID.
                 - reviewed_id (int): The reviewed user's ID.
                 - task_id (int): The task ID.
        """
        _, reviewer_id, reviewed_id, task_id = callback_data.split("|")
        return int(reviewer_id), int(reviewed_id), int(task_id)


def create_group_message_keyboard(
        task_id: int,
        has_files: bool = True,
        is_active: bool = True
):
    builder = InlineKeyboardBuilder()

    if is_active:
        builder.row(
            InlineKeyboardButton(
                text="Взяти замовлення",
                url=f"{BOT_URL}?start={task_id}-take_order"
            )
        )

    if has_files:
        builder.row(
            InlineKeyboardButton(
                text="Ознайомитись з файлами",
                url=f"{BOT_URL}?start={task_id}-check_files"
            )
        )

    return builder.as_markup()


def create_accepting_deal(
        client_id: int,
        executor_id: int,
        task_id: int,
        executor_username: str = None
):
    builder = InlineKeyboardBuilder()

    builder.add(
        InlineKeyboardButton(
            text="Прийняти замовлення",
            callback_data=f"create-chat|{client_id}|{executor_id}|{task_id}|{executor_username}"
        ),
        InlineKeyboardButton(
            text="Відмовити",
            callback_data=f"deal_minus|{task_id}|{client_id}|{executor_id}"
        )
    )

    return builder.as_markup()


def create_group_message_keyboard_telethon(task_id: int, has_files: bool = True, is_active: bool = True):
    buttons = []

    if is_active:
        buttons.append(
            KeyboardButtonRow(
                buttons=[Button.url(text="Взяти замовлення",
                                    url=f"{BOT_URL}?start={task_id}-take_order")]
            )
        )

    if has_files:
        buttons.append(
            KeyboardButtonRow(
                buttons=[Button.url(text="Ознайомитись з файлами",
                                    url=f"{BOT_URL}?start={task_id}-check_files")]
            )
        )

    return ReplyInlineMarkup(rows=buttons)


def create_review_reply_markup(reviewer_id: int, reviewed_id: int, task_id: int):
    constructor = CallbackConstructorReview(reviewer_id=reviewer_id, reviewed_id=reviewed_id, task_id=task_id)

    buttons_row = KeyboardButtonRow(
        buttons=[
            Button.inline(
                text="Оцінити",
                data="accept-review" + constructor.construct_callback_data()
            ),
            Button.inline(
                text="Відмовитись",
                data="reject-review"
            )
        ]
    )

    return ReplyInlineMarkup(rows=[buttons_row])


def create_payment_msg(payment_url: str):
    builder = InlineKeyboardBuilder()

    builder.add(
        InlineKeyboardButton(
            text="Перейти до оплати",
            url=payment_url,
        )
    )

    return builder.as_markup()


def create_chats_inline_kbd(chats: ChatsList, user_type: UserType):
    builder = InlineKeyboardBuilder()

    for chat in chats:
        builder.add(
            InlineKeyboardButton(
                text=chat.group_name,
                url=f"{CHAT_BOT_URL}?start=chat-{chat.id}" if user_type == UserType.client else chat.invite_link
            )
        )

    return builder.as_markup()


def create_accept_offer_msg(task_id: int, transaction_id: int, amount: decimal.Decimal, receiver_id: int):
    builder = InlineKeyboardBuilder()

    builder.add(
        InlineKeyboardButton(
            text="Підтвердити виконання",
            callback_data=f"accept_offer|{transaction_id}|{task_id}|{amount}|{receiver_id}"
        )
    )

    return builder.as_markup()
