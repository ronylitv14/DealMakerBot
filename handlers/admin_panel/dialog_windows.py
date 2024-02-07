from aiogram_dialog.dialog import Dialog, DialogManager
from aiogram_dialog.window import Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Back, Cancel, Row

from handlers.admin_panel.window_states import *
from handlers.admin_panel.window_widgets import TelegramBtns, TelegramInputs

from database_api.components.executors import ExecutorsList
from database_api.components.users import UserResponseList
from database_api.components.withdrawals import WithdrawalRequestList
from database_api.components.tickets import TicketsList

application_text = Format("Ім'я користувача: {dialog_data[username]}\n"
                          "Нік в телеграм: @{dialog_data[tg_username]}\n\n"
                          "Теги для виконавця: \n\n{dialog_data[tags]}\n\n"
                          "Опис власної роботи: \n\n{dialog_data[desc]}")

user_text = Format("Ім'я користувача: {dialog_data[username]}\n"
                   "Нік у телеграмі: {dialog_data[tg_username]}\n\n"
                   "Наявний баланс: <b>{dialog_data[balance_amount]}</b>")


def create_back_button(btn_text: str):
    return Back(Const(btn_text))


def create_cancel_button(btn_text: str):
    return Cancel(Const(btn_text))


async def get_applications_data(**kwargs):
    manager: DialogManager = kwargs.get("dialog_manager")
    applications = manager.start_data.get("applications")

    displayed_result = []

    if applications and isinstance(applications, dict):
        applications = ExecutorsList(**applications)
        for ind, application in enumerate(applications):
            displayed_result.append((application, ind))

    return {
        "applications": displayed_result if displayed_result else [("Немає заявок", -1)]
    }


async def get_users_data(**kwargs):
    manager: DialogManager = kwargs.get("dialog_manager")
    users = manager.start_data.get("users")

    displayed_result = []
    if users and isinstance(users, dict):
        users = UserResponseList(**users)
        for ind, user in enumerate(users):
            displayed_result.append((user, ind))

    return {
        "users": displayed_result if displayed_result else [("Немає користувачів", -1)]
    }


async def get_requests_data(**kwargs):
    manager: DialogManager = kwargs.get("dialog_manager")
    requests = manager.start_data.get("requests")

    displayed_result = []
    if requests and isinstance(requests, dict):
        requests = WithdrawalRequestList(**requests)
        for ind, request in enumerate(requests):
            displayed_result.append((request, ind))

    return {
        "requests": displayed_result if displayed_result else [("Немає заявок", -1)]
    }


async def get_tickets_data(**kwargs):
    manager: DialogManager = kwargs.get("dialog_manager")
    tickets = manager.start_data.get("tickets")

    displayed_result = []
    if tickets and isinstance(tickets, dict):
        tickets = TicketsList(**tickets)
        for ind, ticket in enumerate(tickets):
            displayed_result.append((ticket, ind))

    return {
        "tickets": displayed_result if displayed_result else [("Немає тікетів", -1)]
    }


main_window = Window(
    Const("Панель адміна"),
    TelegramBtns.btn_exec_applications,
    TelegramBtns.btn_create_chat,
    TelegramBtns.btn_users_profiles,
    TelegramBtns.btn_request_applications,
    TelegramBtns.btn_watch_tickets,
    TelegramBtns.btn_start_inactive_chat_dialog,
    create_cancel_button("Вийти"),
    state=AdminPanel.main_panel
)

# Applications

watch_applications_window = Window(
    Const("Перегляд заявок"),
    TelegramInputs.applications_select,
    create_cancel_button("Назад"),
    state=WatchExecutorApplication.watch_applications,
    getter=get_applications_data
)

review_application_window = Window(
    application_text,
    TelegramBtns.btn_accept_executor,
    TelegramBtns.btn_reject_executor,
    state=WatchExecutorApplication.review_application
)

# Tickets

watch_tickets_window = Window(
    Const("Перегляд тікетів"),
    TelegramInputs.tickets_select,
    create_cancel_button("Вийти"),
    state=WatchTickets.watch_applications,
    getter=get_tickets_data
)

review_ticket_window = Window(
    Format("Огляд тікету\n\n"
           "Ім'я користувача в системі: <b>{dialog_data[username]}</b>\n"
           "Нік в телеграм: @{dialog_data[tg_username]}\n\n"
           "Категорія тікету: <b>{dialog_data[subject]}</b>\n\n"
           "Опис:\n\n<i>{dialog_data[desc]}</i>"),
    TelegramBtns.btn_close_ticket,
    Row(
        create_back_button("Вийти"),
        create_back_button("Назад")
    ),
    state=WatchTickets.review_application,
    parse_mode="HTML"
)

# Withdrawal requests

withdrawal_text = Format(
    "Запит на виведення: №{dialog_data[request_id]}\n"
    "Теперішній баланс користувача: {dialog_data[balance]}\n\n"
    "Сума до виведення: {dialog_data[request_amount]}\n\n"
    "Сума комісії: {dialog_data[commission]}\n\n"
    "Карта для виведення коштів: {dialog_data[card_number]}"
)

watch_requests_window = Window(
    Format("Запити на виведення!"),
    TelegramInputs.withdrawal_select,
    create_cancel_button("До головного меню"),
    state=WatchMoneyRetrieval.watch_applications,
    getter=get_requests_data
)

review_requests_window = Window(
    withdrawal_text,
    TelegramBtns.btn_accept_withdraw,
    TelegramBtns.btn_reject_withdraw,
    create_back_button("Назад"),
    state=WatchMoneyRetrieval.review_application
)

add_invoice_window = Window(
    Format("Тут потрібно додати № квитанції сплатити грошей для користувача!"),
    TelegramInputs.input_invoice_id,
    TelegramBtns.btn_save_without_invoice,
    create_back_button("Вийти"),
    state=WatchMoneyRetrieval.add_invoice_id
)

# Users logic

all_users_window = Window(
    Format("Всі користувачі, окрім адмінів"),
    TelegramInputs.users_selected,
    create_cancel_button("До головного меню"),
    state=UserData.all_users,
    getter=get_users_data
)

single_user_window = Window(
    user_text,
    TelegramBtns.btn_balance,
    TelegramBtns.btn_user_management,
    TelegramBtns.btn_get_report,
    create_back_button("Назад"),
    state=UserData.single_user,
    parse_mode="HTML"
)

# Balance changing
change_balance_window = Window(
    Format("Зміна балансу"),
    TelegramInputs.input_new_balance,
    create_cancel_button("До меню користувачів"),
    state=ChangeUserBalance.change_balance
)

accept_balance_window = Window(
    Format("Ім'я користувача: {dialog_data[user]}\n\n"
           "Новий баланс для користувача: {dialog_data[new_balance]}\n"),
    TelegramBtns.btn_accept_balance,
    create_back_button("Назад"),
    state=ChangeUserBalance.accept_new_balance
)


def create_admin_panel_dialog():
    return Dialog(
        main_window
    )


def create_application_dialog():
    return Dialog(
        watch_applications_window,
        review_application_window
    )


def create_users_dialog():
    return Dialog(
        all_users_window,
        single_user_window
    )


def create_balance_dialog():
    return Dialog(
        change_balance_window,
        accept_balance_window
    )


def create_withdraw_dialog():
    return Dialog(
        watch_requests_window,
        review_requests_window,
        add_invoice_window
    )


def create_ticket_dialog():
    return Dialog(
        watch_tickets_window,
        review_ticket_window
    )
