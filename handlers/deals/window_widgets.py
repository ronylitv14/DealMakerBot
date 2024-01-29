import operator
from typing import Any

from aiogram.types import CallbackQuery
from aiogram_dialog.widgets.kbd import Button, Select, Back, ScrollingGroup
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.dialog import DialogManager

from database_api.components.tasks import TaskModel
from handlers.deals.button_callbacks import ButtonCallbacks
from handlers.utils.start_action_handler import create_files_reply
from keyboards.inline_keyboards import create_accepting_deal


async def on_nickname_selected(callback: CallbackQuery, widget: Any,
                               manager: DialogManager, item_id: str):
    if item_id == "-1":
        return await callback.message.answer(text="На даний момент немає доступних користувачів!")

    users = manager.dialog_data.get("users")
    manager.dialog_data["nickname"] = users[int(item_id)]
    manager.dialog_data["subject_title"] = []
    manager.dialog_data["type"] = []
    manager.dialog_data["docs"] = []
    manager.dialog_data["executor_id"] = users[int(item_id)].telegram_id
    await manager.next()


async def on_deal_selected(callback: CallbackQuery, widget: Any,
                           manager: DialogManager, item_id: str, **kwargs):
    if item_id == "-1":
        return await callback.message.answer(text="Поки вам нових угод не приходило!")

    deals = manager.dialog_data.get("returned_deals")

    selected_deal: TaskModel = deals[int(item_id)]
    subjects = ", ".join(selected_deal.subjects)
    work_type = ", ".join(selected_deal.work_type)

    await callback.message.answer(
        text="Ось дані щодо запропонованої угоди:\n\n"
             f"Номер замовлення: {selected_deal.task_id}\n"
             f"Теги до завдання:<b>{subjects}</b>\n"
             f"Вид завдання: <b>{work_type}</b>\n"
             f"Ціна: <b>{selected_deal.price}</b>\n"
             f"Опис: \n\n<b>{selected_deal.description}</b>",
        parse_mode="HTML",
    )

    if selected_deal.files:
        await create_files_reply(
            files=selected_deal.files,
            files_type=selected_deal.files_type,
            message=callback.message
        )

    await callback.message.answer(
        text="Ви готові взяти це замовлення? Після прийняття вам буде запропоновано перейти до чату для "
             "обговорення кінцевої ціни!",
        reply_markup=create_accepting_deal(
            client_id=selected_deal.client_id,
            executor_id=selected_deal.executor_id,
            task_id=selected_deal.task_id,
            executor_username=selected_deal.executor_id
        )
    )

    await manager.done()


class TelegramInputs:
    input_nickname = ScrollingGroup(
        Select(
            text=Format("{item[0]}"),
            id="s_nickname",
            item_id_getter=operator.itemgetter(1),
            items="result",
            on_click=on_nickname_selected
        ),
        id="sc_nickname",
        height=5,
        width=2
    )

    input_deal = ScrollingGroup(
        Select(
            text=Format("{item[0]}"),
            id="s_deal",
            item_id_getter=operator.itemgetter(1),
            items="all_deals",
            on_click=on_deal_selected
        ),
        id="sc_deal",
        height=5,
        width=1
    )


class TelegramBtns:
    btn_create_deal = Button(Const("Створити угоду"), id="b_create_deal", on_click=ButtonCallbacks.create_deal)
    btn_watch_deals = Button(Const("Переглянути заявки"), id="b_watch_deals", on_click=ButtonCallbacks.watch_deals)

    btn_cancel = Button(Const("Відмінити"), id="b_cancel", on_click=ButtonCallbacks.cancel_dialog)
    btn_back_main_dialog = Button(Const("Вийти"), id="btn_back_main", on_click=ButtonCallbacks.cancel_subdialog)
    btn_back = Back(Const("Назад"))
    btn_save_deal = Button(Const("Зберегти"), id="save_deal", on_click=ButtonCallbacks.save_deal)
