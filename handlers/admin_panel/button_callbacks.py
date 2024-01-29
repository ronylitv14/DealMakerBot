import decimal
from datetime import datetime
from uuid import uuid1
from aiogram.types import CallbackQuery, Message, BufferedInputFile
from aiogram_dialog.dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.api.entities import StartMode, ShowMode

from handlers.admin_panel.transactions_output.report import create_output_file
from handlers.admin_panel.window_states import WatchExecutorApplication, UserData, ChangeUserBalance, BanUser, \
    WatchMoneyRetrieval, WatchTickets

from handlers.admin_panel.create_new_chat.dialog_states import CreatingCustomChat
from handlers.admin_panel.inactive_chat.dialog_states import InactiveChat
from database_api.components.users import Users, UserResponse, UserResponseList
from database_api.components.executors import Executors, ExecutorModel, ProfileStatus
from database_api.components.transactions import Transactions, TransactionModel, TransactionStatus, TransactionType, \
    TransactionList
from database_api.components.tickets import Tickets, TicketStatus
from database_api.components.withdrawals import Withdrawals, WithdrawalStatus
from database_api.components.balance import Balance, BalanceAction


async def watch_applications(retrieve_data_func, states_group, manager: DialogManager, data_name: str,
                             mode: StartMode = StartMode.NEW_STACK):
    applications = await retrieve_data_func.do_request()

    await manager.start(
        state=states_group.watch_applications,
        mode=mode,
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
    async def process_invoice_id(message: Message, widget: MessageInput, manager: DialogManager):
        transaction_obj: TransactionModel = manager.dialog_data.get("transaction_obj")
        invoice_id = message.text
        if not message.text:
            return await message.answer("Потрібно додати номер транзакції до карти обов'язково!")

        if len(invoice_id) not in range(18, 25):
            return await message.answer("Скоріш за все це неправильний метод валідації!")

        transaction_obj.invoice_id = invoice_id
        transaction_obj.transaction_status = TransactionStatus.completed

        await Transactions().save_transaction_data(
            **transaction_obj.model_dump()
        ).do_request()

        await message.answer(
            text=f"Додано <i>invoice_id</i> {invoice_id} до запиту на виведення коштів!",
            parse_mode="HTML"
        )

        await manager.done()


class ButtonCallbacksMoney:
    @staticmethod
    async def get_money_withdraw(callback: CallbackQuery, button: Button, manager: DialogManager):
        await watch_applications(
            retrieve_data_func=Withdrawals().get_withdrawals_data(),
            states_group=WatchMoneyRetrieval,
            manager=manager,
            data_name="requests",
            mode=StartMode.NORMAL
        )

    @staticmethod
    async def accept_money_withdraw(callback: CallbackQuery, button: Button, manager: DialogManager):
        receiver_id = int(manager.dialog_data.get("request_user_id"))
        amount = decimal.Decimal(manager.dialog_data.get("request_amount"))
        commission = manager.dialog_data.get("commission")
        request_id = manager.dialog_data.get("request_id")

        transaction_obj = TransactionModel(
            invoice_id="",
            amount=amount,
            transaction_type=TransactionType.withdrawal,
            transaction_status=TransactionStatus.pending,
            receiver_id=receiver_id,
            commission=commission
        )

        manager.dialog_data["transaction_obj"] = transaction_obj

        await Withdrawals().update_withdrawal_request(
            request_id=request_id,
            new_status=WithdrawalStatus.processed,
            admin_id=callback.from_user.id,
        ).do_request()

        await manager.switch_to(WatchMoneyRetrieval.add_invoice_id)

    @staticmethod
    async def reject_money_withdrawal(callback: CallbackQuery, button: Button, manager: DialogManager):
        request_id = manager.dialog_data.get("request_id")
        receiver_id = int(manager.dialog_data.get("request_user_id"))
        amount = decimal.Decimal(manager.dialog_data.get("request_amount"))
        commission = manager.dialog_data.get("commission")

        await Withdrawals().update_withdrawal_request(
            request_id=request_id,
            new_status=WithdrawalStatus.rejected,
            admin_id=callback.from_user.id,
        ).do_request()

        await Balance().perform_fund_transfer(
            user_id=receiver_id,
            amount=amount + commission,
            action=BalanceAction.replenishment
        ).do_request()

        await callback.bot.send_message(
            chat_id=receiver_id,
            text="<b>Вам було відмовлено у виведенні коштів!</b>\n\n"
                 "Зверніться до когось з адміністраторів каналу для вирішення вашого випадку!",
            parse_mode="HTML"
        )

        await manager.done()

    @staticmethod
    async def save_without_invoice_id(callback: CallbackQuery, button: Button, manager: DialogManager):
        transaction_obj: TransactionModel = manager.dialog_data.get("transaction_obj")
        invoice_id = str(uuid1())
        transaction_obj.invoice_id = invoice_id
        transaction_obj.transaction_status = TransactionStatus.completed

        await Transactions().save_transaction_data(
            **transaction_obj.model_dump()
        ).do_request()

        await callback.message.answer(
            text=f"Додано <i>invoice_id</i> {invoice_id} до запиту на виведення коштів!",
            parse_mode="HTML"
        )

        await manager.done()


class ButtonCallbacks:
    @staticmethod
    async def get_executors_applications(callback: CallbackQuery, button: Button, manager: DialogManager):

        await watch_applications(
            retrieve_data_func=Executors().get_executor_applications(),
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
            retrieve_data_func=Tickets().get_ticket_json(),
            states_group=WatchTickets,
            manager=manager,
            data_name="tickets",
            mode=StartMode.NORMAL
        )

    @staticmethod
    async def get_users_profiles(callback: CallbackQuery, button: Button, manager: DialogManager):
        # users = await get_usual_users()

        users: UserResponseList = await Users().get_all_users_except_admins().do_request()

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

        await Tickets().update_ticket_status(
            ticket_id=ticket.ticket_id,
            admin_id=callback.from_user.id,
            new_status=TicketStatus.closed
        ).do_request()

        await manager.done()

    @staticmethod
    async def accept_executor_application(callback: CallbackQuery, button: Button, manager: DialogManager):
        applicant: ExecutorModel = manager.dialog_data.get("applicant")

        if applicant.profile_state == ProfileStatus.accepted:
            return await callback.message.answer(
                text="<b>Цей виконавець вже був прийнятий раніше</b>",
                parse_mode="HTML"
            )

        if applicant:
            await Executors().update_executor_status(
                executor_id=applicant.executor_id,
                new_status=ProfileStatus.accepted
            ).do_request()

        await callback.message.answer(
            text="Користувач успішно оновлений!"
        )

        await manager.done()

    @staticmethod
    async def reject_executor_application(callback: CallbackQuery, button: Button, manager: DialogManager):
        applicant: ExecutorModel = manager.dialog_data.get("applicant")

        if applicant:
            await Executors().update_executor_status(
                executor_id=applicant.executor_id,
                new_status=ProfileStatus.rejected
            ).do_request()

        await callback.message.answer(
            text="Користувачу відмовлено в доступі до роботи виконавцем!"
        )

        await manager.done()

    @staticmethod
    async def change_balance(callback: CallbackQuery, button: Button, manager: DialogManager):
        user: UserResponse = manager.dialog_data.get("user")

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
        user: UserResponse = manager.start_data.get("user")

        if new_amount is None:
            return await callback.message.answer(text="Щось не так з новим значенням балансу!")

        await Balance().reset_user_balance(
            user_id=user.telegram_id,
            new_amount=new_amount
        ).do_request()

        await manager.done()

    @staticmethod
    async def get_bans_management(callback: CallbackQuery, button: Button, manager: DialogManager):
        user: UserResponse = manager.dialog_data.get("user")

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
        user: UserResponse = manager.dialog_data.get("user")
        transactions = await Transactions().get_user_transactions(user.telegram_id).do_request()
        if isinstance(transactions, TransactionList):
            file = create_output_file(
                transactions=transactions
            )

            await callback.message.bot.send_document(
                chat_id=callback.from_user.id,
                document=BufferedInputFile(file.getvalue(),
                                           filename=f"{user.username}_transactions_{datetime.now()}.xlsx")
            )
            return
        return await callback.message.answer("По даному користувачу немає доступних транзакцій!")


class CallbacksDeactivationChat:
    @staticmethod
    async def start_deactivation_chat_dialog(callback: CallbackQuery, button: Button, manager: DialogManager):
        await manager.start(
            state=InactiveChat.query_chat,
            mode=StartMode.NORMAL
        )
