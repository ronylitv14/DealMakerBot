from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from telethon import Button
from telethon.types import ReplyInlineMarkup, KeyboardButtonRow


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
                url=f"https://t.me/newdopomogatestbot?start={task_id}-take_order"
            )
        )

    if has_files:
        builder.row(
            InlineKeyboardButton(
                text="Ознайомитись з файлами",
                url=f"https://t.me/newdopomogatestbot?start={task_id}-check_files"
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
                buttons=[Button.url("Взяти замовлення",
                                    f"https://t.me/newdopomogatestbot?start={task_id}-take_order")]
            )
        )

    if has_files:
        buttons.append(
            KeyboardButtonRow(
                buttons=[Button.url("Ознайомитись з файлами",
                                    f"https://t.me/newdopomogatestbot?start={task_id}-check_files")]
            )
        )

    return ReplyInlineMarkup(rows=buttons)


def create_payment_msg(payment_url: str):
    builder = InlineKeyboardBuilder()

    builder.add(
        InlineKeyboardButton(
            text="Перейти до оплати",
            url=payment_url,

        )
    )

    return builder.as_markup()
