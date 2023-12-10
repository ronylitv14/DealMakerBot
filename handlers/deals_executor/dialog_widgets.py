import operator
from typing import Any

from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Select, ScrollingGroup
from aiogram_dialog.widgets.text import Format
from aiogram_dialog.dialog import DialogManager
from aiogram.enums import ContentType
from aiogram.types import CallbackQuery

from database.models import User, TaskStatus, PropositionBy
from database.crud import save_task_to_db
from handlers.deals_executor.button_callbacks import InputCallbacks


async def on_client_selected(callback: CallbackQuery, widget: Any,
                             manager: DialogManager, item_id: str):
    if item_id == "-1":
        return await callback.answer(text="Не знайдено таких користувачів! Поверніться назад і спробуйте ще раз!")

    users = manager.dialog_data.get("users")
    user: User = users[int(item_id)]

    await save_task_to_db(
        client_id=user.telegram_id,
        executor_id=callback.from_user.id,
        status=TaskStatus.active,
        description="Без опису",
        proposed_by=PropositionBy.executor,
        subjects=["Інше"],
        work_type=["Інше"],
        price="Договірна"
    )

    await callback.bot.send_message(
        chat_id=user.telegram_id,
        text="<b>У вас є нова угода!</b> Зайдіть у розділ 'Угоди' і перегляньте запропоновані угоди!",
        parse_mode="HTML"
    )

    await manager.done()

    await callback.message.answer(
        text="Угода надіслана!"
    )

class TelegramInputs:
    input_username = MessageInput(
        func=InputCallbacks.get_all_possible_users,
        content_types=ContentType.TEXT
    )

    select_user = ScrollingGroup(
        Select(
            text=Format("{item[0]}"),
            on_click=on_client_selected,
            item_id_getter=operator.itemgetter(1),
            items="users",
            id="s_users"
        ),
        id="sg_users",
        height=6,
        width=1
    )


class TelegramBtns:
    pass
