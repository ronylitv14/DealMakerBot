import operator
from typing import Any, List

from aiogram.types import CallbackQuery
from aiogram.types import ContentType

from aiogram_dialog.dialog import DialogManager
from aiogram_dialog.api.entities import StartMode
from aiogram_dialog.widgets.kbd import Button, ScrollingGroup, Select
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.text import Const, Format

from handlers.admin_panel.button_callbacks import ButtonCallbacks, InputCallbacks, ButtonCallbacksMoney
from handlers.admin_panel.window_states import WatchExecutorApplication
from handlers.utils.start_action_handler import create_files_reply
from database.models import Executor, User, Balance, WithdrawalRequest, UserTicket, TicketStatus
from database.crud import get_user_auth, get_user_balance


async def on_application_selected(callback: CallbackQuery, widget: Any,
                                  manager: DialogManager, item_id: str):
    if item_id == "-1":
        return await callback.message.answer(text="<b>На даний момент заявок немає!</b>", parse_mode="HTML")

    applications: List[Executor] = manager.start_data.get("applications")
    application: Executor = applications[int(item_id)]

    user: User = await get_user_auth(application.user_id)

    tags = [tag.strip().replace(" ", "_") for tag in application.tags]

    manager.dialog_data["tags"] = "#" + " #".join(tags)
    manager.dialog_data["desc"] = application.description
    manager.dialog_data["username"] = user.username
    manager.dialog_data["tg_username"] = user.telegram_username
    manager.dialog_data["applicant"] = application

    await manager.next()

    has_files = await create_files_reply(
        files_type=application.work_files_type,
        files=application.work_examples,
        message=callback.message
    )

    if not has_files:
        await callback.message.answer(
            text="<b>Виконавець не надав ніяких прикладів робіт тощо!</b>",
            parse_mode="HTML"
        )


async def on_user_selected(callback: CallbackQuery, widget: Any,
                           manager: DialogManager, item_id: str):
    if item_id == "-1":
        return await callback.message.answer(text="<b>На даний момент користувачів немає!</b>", parse_mode="HTML")

    users: List[User] = manager.start_data.get("users")
    user: User = users[int(item_id)]

    balance: Balance = await get_user_balance(user_id=user.telegram_id)

    manager.dialog_data["user"] = user
    manager.dialog_data["username"] = user.username
    manager.dialog_data["tg_username"] = user.telegram_username
    manager.dialog_data["balance_amount"] = balance.balance_money

    await manager.next()


async def on_withdrawal_selected(callback: CallbackQuery, widget: Any,
                                 manager: DialogManager, item_id: str):
    if item_id == "-1":
        return await callback.message.answer(text="<b>Немає нових запитів!</b>", parse_mode="HTML")

    requests: List[WithdrawalRequest] = manager.start_data.get("requests")
    request: WithdrawalRequest = requests[int(item_id)]

    balance: Balance = await get_user_balance(user_id=request.user_id)

    manager.dialog_data["balance"] = balance.balance_money
    manager.dialog_data["request_user_id"] = request.user_id
    manager.dialog_data["request_id"] = request.request_id
    manager.dialog_data["request_amount"] = request.amount
    manager.dialog_data["commission"] = request.commission
    manager.dialog_data["card_number"] = request.payment_method

    await manager.next()


async def on_ticket_selected(callback: CallbackQuery, widget: Any,
                             manager: DialogManager, item_id: str):
    if item_id == "-1":
        return await callback.message.answer(text="<b>Немає нових тікетів!</b>", parse_mode="HTML")

    tickets: List[UserTicket] = manager.start_data.get("tickets")
    ticket: UserTicket = tickets[int(item_id)]

    if ticket.status == TicketStatus.closed:
        return await callback.answer(text="Цей тікет вже закритий!", show_alert=True)

    user: User = await get_user_auth(ticket.user_id)

    manager.dialog_data["username"] = user.username
    manager.dialog_data["tg_username"] = user.telegram_username
    manager.dialog_data["subject"] = ticket.subject
    manager.dialog_data["desc"] = ticket.description
    manager.dialog_data["ticket"] = ticket

    await manager.next()


class TelegramInputs:
    applications_select = ScrollingGroup(
        Select(
            text=Format("{item[0]}"),
            on_click=on_application_selected,
            items="applications",
            item_id_getter=operator.itemgetter(1),
            id="select_applications"
        ),
        id="scroll_applications",
        height=6,
        width=1,
    )

    users_selected = ScrollingGroup(
        Select(
            text=Format("{item[0]}"),
            on_click=on_user_selected,
            items="users",
            item_id_getter=operator.itemgetter(1),
            id="select_users"
        ),
        id="scroll_users",
        height=6,
        width=1
    )

    withdrawal_select = ScrollingGroup(
        Select(
            text=Format("{item[0]}"),
            on_click=on_withdrawal_selected,
            item_id_getter=operator.itemgetter(1),
            id="select_withdrawal",
            items="requests"
        ),
        id="scroll_requests",
        height=6,
        width=1
    )

    tickets_select = ScrollingGroup(
        Select(
            text=Format("{item[0]}"),
            item_id_getter=operator.itemgetter(1),
            items="tickets",
            id="select_tickets",
            on_click=on_ticket_selected
        ),
        height=6,
        width=1,
        id="scroll_tickets"
    )

    input_new_balance = MessageInput(
        func=InputCallbacks.process_balance_data,
        content_types=ContentType.TEXT
    )

    input_invoice_id = MessageInput(
        func=InputCallbacks.process_invoice_id,
        content_types=ContentType.TEXT
    )


class TelegramBtns:
    btn_exec_applications = Button(Const("Заявки виконавців"), id="btn_applications",
                                   on_click=ButtonCallbacks.get_executors_applications)
    btn_accept_executor = Button(Const("Прийняти заявку"), id="btn_accept_exec",
                                 on_click=ButtonCallbacks.accept_executor_application)
    btn_reject_executor = Button(Const("Відхилити заявку"), id="btn_reject_exec",
                                 on_click=ButtonCallbacks.reject_executor_application)

    btn_users_profiles = Button(Const("Робота з користувачами"), id="btn_users",
                                on_click=ButtonCallbacks.get_users_profiles)
    btn_balance = Button(Const("Змінити баланс"), id="btn_balance", on_click=ButtonCallbacks.change_balance)
    btn_user_management = Button(Const("Бани та попередження користувачів"), id="btn_management",
                                 on_click=ButtonCallbacks.get_bans_management)

    btn_accept_balance = Button(Const("Підтвердити баланс"), id="btn_accept_balance",
                                on_click=ButtonCallbacks.accept_new_balance)

    btn_request_applications = Button(Const("Заявки на виведення коштів"), id="btn_requests",
                                      on_click=ButtonCallbacksMoney.get_money_withdraw)

    btn_accept_withdraw = Button(Const("Підтвердити вивід коштів"), id="btn_accept_withdrawal",
                                 on_click=ButtonCallbacksMoney.accept_money_withdraw)

    btn_reject_withdraw = Button(Const("Відмовити у виведенні коштів"), id="btn_reject_withdrawal",
                                 on_click=ButtonCallbacksMoney.reject_money_withdrawal)

    btn_watch_tickets = Button(Const("Перегляд тікетів користувачів"), id="btn_tickets",
                               on_click=ButtonCallbacks.get_all_tickets)

    btn_close_ticket = Button(Const("Закрити тікет"), id="btn_close_ticket",
                              on_click=ButtonCallbacks.close_ticket)

    btn_get_report = Button(Const("Звіт по транзакціям"), id="btn_report",
                            on_click=ButtonCallbacks.get_transactions_file)

    btn_create_chat = Button(Const("Створити унікальний чат"), id="btn_create_chat",
                             on_click=ButtonCallbacks.create_unique_chat)
