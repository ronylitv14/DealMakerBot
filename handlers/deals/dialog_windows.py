from typing import List, Any

from aiogram_dialog.window import Window
from aiogram_dialog.widgets.text import Format
from aiogram_dialog.widgets.kbd import Row
from aiogram_dialog.dialog import Dialog, DialogManager
from handlers.states_handler import ClientDialog, ExecutorDialog
from aiogram.fsm.context import FSMContext
from handlers.deals.window_state import CreateDeal, DealsGroup
from handlers.creating_orders import window_widgets as deal_widgets
from handlers.creating_orders.dialog_windows import get_order_type, get_subjects

from handlers.deals.window_widgets import TelegramInputs, TelegramBtns


from database_api.components.tasks import PropositionBy, TasksList, TaskModel
from database_api.components.executors import Executors
from database_api.components.chats import Chats
from database_api.components.users import UserResponseList

proposed_deals_states = {
    ClientDialog.client_state: PropositionBy.executor,
    ExecutorDialog.executor_state: PropositionBy.client
}

users_for_deals = {
    ClientDialog.client_state: Executors().get_all_executors,
    ExecutorDialog.executor_state: Chats().get_recent_clients
}


async def get_nickname_data(**kwargs):
    manager: DialogManager = kwargs.get("dialog_manager")
    cur_state = manager.start_data.get("cur_state")

    get_data_func = users_for_deals[cur_state]
    user_id: int = manager.start_data.get("user_id")

    result = []

    users: UserResponseList = await get_data_func(user_id).do_request()

    if isinstance(users, UserResponseList):
        manager.dialog_data["users"] = users.model_dump(mode="json")

        for ind, user in enumerate(users):
            result.append((user.username, ind))

    return {
        "result": result if result else [("Не знайдено користувачів", -1)]
    }


async def get_deals_data(**kwargs):
    manager: DialogManager = kwargs.get("dialog_manager")

    returned_deals = manager.dialog_data["returned_deals"]

    all_deals = []
    if returned_deals and isinstance(returned_deals, dict):
        returned_deals = TasksList(**returned_deals)

        for ind, deal in enumerate(returned_deals):
            all_deals.append((deal, ind))

    return {
        "all_deals": all_deals if all_deals else [("Немає нових угод", -1)]
    }


main_window = Window(
    Format(
        "Ви перейшли до вкладки з угодами. У вас "
        "є можливітсь обрати чи ви хочете створити нову угоду з вже відомою наперед "
        "людиною чи переглянути запропоновані вам угоди"
    ),
    TelegramBtns.btn_create_deal,
    TelegramBtns.btn_watch_deals,
    TelegramBtns.btn_cancel,
    state=DealsGroup.main_deals
)

watch_deals_window = Window(
    Format("От всі запропоновані вам угоди!"),
    TelegramInputs.input_deal,
    Row(
        TelegramBtns.btn_back,
        TelegramBtns.btn_cancel
    ),
    state=DealsGroup.watch_deals,
    getter=get_deals_data
)

# Creating deal dialog

nickname_window = Window(
    Format("Оберіть з вже перевірених нами виконавців"),
    TelegramInputs.input_nickname,
    TelegramBtns.btn_back_main_dialog,
    state=CreateDeal.choose_nickname,
    getter=get_nickname_data
)

task_type_window = Window(
    Format("Оберіть варіант роботи"),
    deal_widgets.TelegramInputs.order_type_select,
    deal_widgets.TelegramBtns.btn_task_type,
    TelegramBtns.btn_back,
    TelegramBtns.btn_back_main_dialog,
    state=CreateDeal.add_task_type,
    getter=get_order_type
)

subject_window = Window(
    Format("Оберіть потрібний предмет"),
    deal_widgets.TelegramInputs.subject_title_select,
    deal_widgets.TelegramBtns.btn_subject,
    TelegramBtns.btn_back,
    TelegramBtns.btn_back_main_dialog,
    state=CreateDeal.add_subject,
    getter=get_subjects
)

price_window = Window(
    Format("Додайте свою ціну для створення угоди"),
    deal_widgets.TelegramInputs.input_price,
    TelegramBtns.btn_back,
    TelegramBtns.btn_back_main_dialog,
    state=CreateDeal.add_price
)

description_window = Window(
    Format("Тепер додайте опис для свого замовлення"),
    deal_widgets.TelegramInputs.input_desc,
    TelegramBtns.btn_back,
    TelegramBtns.btn_back_main_dialog,
    state=CreateDeal.add_description
)

files_window = Window(
    Format("Тепер додайте файли, якщо потрібно для вашого замовлення"),
    deal_widgets.TelegramInputs.input_docs,
    TelegramBtns.btn_save_deal,
    TelegramBtns.btn_back_main_dialog,
    state=CreateDeal.add_files
)


# async def on_dialog_close(data: Any, dialog_manager: DialogManager):
#     cur_state = dialog_manager.dialog_data.get("cur_state")
#     state: FSMContext = dialog_manager.dialog_data.get("state_obj")
#
#     if state and cur_state:
#         await state.set_state(cur_state)


def create_dialog_client():
    return Dialog(
        nickname_window,
        task_type_window,
        subject_window,
        description_window,
        price_window,
        files_window
    ), Dialog(
        main_window,
        watch_deals_window,
        # on_close=on_dialog_close
    )
