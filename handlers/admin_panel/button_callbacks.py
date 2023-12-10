import decimal
from datetime import datetime

from aiogram import Bot
from aiogram.types import CallbackQuery, Message, BufferedInputFile
from aiogram_dialog.dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.api.entities import StartMode, ShowMode

from handlers.admin_panel.transactions_output.report import create_output_file_1
from handlers.admin_panel.window_states import WatchExecutorApplication, UserData, ChangeUserBalance, BanUser, \
    WatchMoneyRetrieval, WatchTickets

from handlers.admin_panel.create_new_chat.dialog_states import CreatingCustomChat

from database.crud import get_executor_applications, update_application_status, get_usual_users, get_user_balance, \
    create_new_balance, get_user_transactions, get_all_withdrawal_requests, update_balance, BalanceAction, \
    update_withdrawal_request, create_obj_in_db, get_user_tickets, update_ticket_status
from database.models import ProfileStatus, Executor, User, Transaction, TransactionStatus, TransactionType, \
    WithdrawalStatus, TicketStatus


async def watch_applications(retrieve_data_func, states_group, manager: DialogManager, data_name: str):
    applications = await retrieve_data_func()

    await manager.start(
        state=states_group.watch_applications,
        mode=StartMode.NORMAL,
        data={
            data_name: applications
        }
    )


class InputCallbacks:
    @staticmethod
    async def process_balance_data(message: Message, msg_input: MessageInput, manager: DialogManager):
        new_balance = message.text
        try:
            manager.dialog_data["new_balance"] = decimal.Decimal(new_balance)
            manager.dialog_data["user"] = manager.start_data.get("user").telegram_username
            await manager.next()
        except ValueError:
            await message.answer(
                text=f"Введено некоретне значення для балансу: <i>{new_balance}</i>",
                parse_mode="HTML"
            )

    @staticmethod
    async def process_invoice_id(message: Message, msg_input: MessageInput, manager: DialogManager):
        transaction_obj: Transaction = manager.dialog_data.get("transaction_obj")
        invoice_id = message.text

        if not message.text:
            return await message.answer("Потрібно додати номер транзакції до карти обов'язково!")

        transaction_obj.invoice_id = invoice_id

        await create_obj_in_db(
            transaction_obj
        )

        await manager.done()
        await message.answer(
            text=f"Додано <i>invoice_id</i> {invoice_id} до запиту на виведення коштів!"
        )


class ButtonCallbacksMoney:
    @staticmethod
    async def get_money_withdraw(callback: CallbackQuery, button: Button, manager: DialogManager):
        await watch_applications(
            get_all_withdrawal_requests,
            states_group=WatchMoneyRetrieval,
            manager=manager,
            data_name="requests"
        )

    @staticmethod
    async def accept_money_withdraw(callback: CallbackQuery, button: Button, manager: DialogManager):
        receiver_id = int(manager.dialog_data.get("request_user_id"))
        amount = decimal.Decimal(manager.dialog_data.get("request_amount"))
        commission = manager.dialog_data.get("commission")
        request_id = manager.dialog_data.get("request_id")

        transaction_obj = Transaction(
            invoice_id="",
            amount=amount + commission,
            transaction_type=TransactionType.withdrawal,
            transaction_status=TransactionStatus.pending,
            receiver_id=receiver_id,
        )

        manager.dialog_data["transaction_obj"] = transaction_obj

        await update_withdrawal_request(
            request_id=request_id,
            new_status=WithdrawalStatus.processed,
            admin_id=callback.from_user.id,
            processed_time=datetime.utcnow()
        )

        await update_balance(
            user_id=receiver_id,
            amount=amount + commission,
            action=BalanceAction.withdrawal
        )

        await manager.next()

    @staticmethod
    async def reject_money_withdrawal(callback: CallbackQuery, button: Button, manager: DialogManager):
        request_id = manager.dialog_data.get("request_id")
        receiver_id = int(manager.dialog_data.get("request_user_id"))

        await update_withdrawal_request(
            request_id=request_id,
            new_status=WithdrawalStatus.rejected,
            admin_id=callback.from_user.id,
            processed_time=datetime.utcnow()
        )

        await callback.bot.send_message(
            chat_id=receiver_id,
            text="<b>Вам було відмовлено у виведенні коштів!</b>\n\n"
                 "Зверніться до когось з адміністраторів каналу для вирішення вашого випадку!",
            parse_mode="HTML"
        )

        await manager.done()


class ButtonCallbacks:
    @staticmethod
    async def get_executors_applications(callback: CallbackQuery, button: Button, manager: DialogManager):
        # applications = await get_executor_applications()
        #
        # await manager.start(
        #     state=WatchExecutorApplication.watch_applications,
        #     mode=StartMode.NORMAL,
        #     show_mode=ShowMode.SEND,
        #     data={
        #         "applications": applications
        #     }
        # )

        await watch_applications(
            get_executor_applications,
            states_group=WatchExecutorApplication,
            manager=manager,
            data_name="applications"
        )

    @staticmethod
    async def create_unique_chat(callback: CallbackQuery, button: Button, manager: DialogManager):
        await manager.start(
            state=CreatingCustomChat.query_executor,
            mode=StartMode.NORMAL
        )

    @staticmethod
    async def get_all_tickets(callback: CallbackQuery, button: Button, manager: DialogManager):
        await watch_applications(
            get_user_tickets,
            states_group=WatchTickets,
            manager=manager,
            data_name="tickets"
        )

    @staticmethod
    async def get_users_profiles(callback: CallbackQuery, button: Button, manager: DialogManager):
        users = await get_usual_users()

        await manager.start(
            state=UserData.all_users,
            mode=StartMode.NORMAL,
            show_mode=ShowMode.SEND,
            data={
                "users": users
            }
        )

    @staticmethod
    async def close_ticket(callback: CallbackQuery, button: Button, manager: DialogManager):
        ticket = manager.dialog_data.get("ticket")
        await update_ticket_status(
            ticket_id=ticket.ticket_id,
            admin_id=callback.from_user.id,
            new_status=TicketStatus.closed
        )
        await manager.done()

    @staticmethod
    async def accept_executor_application(callback: CallbackQuery, button: Button, manager: DialogManager):
        applicant: Executor = manager.dialog_data.get("applicant")

        if applicant.profile_state == ProfileStatus.accepted:
            return await callback.message.answer(
                text="<b>Цей виконавець вже був прийнятий раніше</b>",
                parse_mode="HTML"
            )

        if applicant:
            await update_application_status(
                executor_id=applicant.executor_id,
                new_profile_state=ProfileStatus.accepted
            )

        await callback.message.answer(
            text="Користувач успішно оновлений!"
        )

        await manager.done()

    @staticmethod
    async def reject_executor_application(callback: CallbackQuery, button: Button, manager: DialogManager):
        applicant: Executor = manager.dialog_data.get("applicant")

        if applicant:
            await update_application_status(
                executor_id=applicant.executor_id,
                new_profile_state=ProfileStatus.rejected
            )

        await callback.message.answer(
            text="Користувачу відмовлено в доступі до роботи виконавцем!"
        )

        await manager.done()

    @staticmethod
    async def change_balance(callback: CallbackQuery, button: Button, manager: DialogManager):
        user: User = manager.dialog_data.get("user")

        await manager.start(
            state=ChangeUserBalance.change_balance,
            mode=StartMode.NORMAL,
            show_mode=ShowMode.SEND,
            data={
                "user": user,
            }
        )

    @staticmethod
    async def accept_new_balance(callback: CallbackQuery, button: Button, manager: DialogManager):
        new_amount = manager.dialog_data.get("new_balance")
        user: User = manager.start_data.get("user")

        if new_amount is None:
            return await callback.message.answer(text="Щось не так з новим значенням балансу!")

        await create_new_balance(
            user_id=user.telegram_id,
            new_amount=new_amount
        )

        await manager.done()

    @staticmethod
    async def get_bans_management(callback: CallbackQuery, button: Button, manager: DialogManager):
        user: User = manager.dialog_data.get("user")

        await manager.start(
            state=BanUser.main_window,
            mode=StartMode.NORMAL,
            show_mode=ShowMode.SEND,
            data={
                "user": user
            }
        )

    @staticmethod
    async def get_transactions_file(callback: CallbackQuery, button: Button, manager: DialogManager):
        user: User = manager.dialog_data.get("user")
        transactions = await get_user_transactions(user.telegram_id)

        file = create_output_file_1(
            transactions=transactions
        )

        await callback.message.bot.send_document(
            chat_id=callback.from_user.id,
            document=BufferedInputFile(file.getvalue(),
                                       filename=f"{user.telegram_id}_transactions_{datetime.now()}.xlsx")
        )
