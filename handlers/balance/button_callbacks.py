import decimal
import os
from aiogram.types import CallbackQuery, Message
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.dialog import DialogManager

from handlers.states_handler import ExecutorDialog
from handlers.balance.window_state import BalanceGroup, WithdrawingMoneySub

from keyboards.inline_keyboards import create_payment_msg
from keyboards.clients import create_keyboard_client
from keyboards.executors import create_keyboard_executor

from utils.dialog_texts import redirect_payment_url
from utils.bank_card_utils import is_valid_card, format_card_number
from handlers.utils.payment_system import BodyInfo, HeaderInfo, get_invoice_payment_link

from database_api.components.users import Users, UserResponse
from database_api.components.balance import Balance, BalanceModel, BalanceAction
from database_api.components.transactions import Transactions, TransactionStatus, TransactionType
from database_api.components.withdrawals import Withdrawals, WithdrawalStatus

from dotenv import load_dotenv

load_dotenv()

X_TOKEN = os.getenv("X_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
COMMISSION = decimal.Decimal("0.03")
TG_GROUP_NAME = os.getenv("TG_GROUP_NAME")


class ButtonCallbacks:
    @staticmethod
    async def add_money(callback: CallbackQuery, button: Button, manager: DialogManager):
        await manager.switch_to(BalanceGroup.adding_money)

    @staticmethod
    async def process_money_adding(message: Message, input_widget: MessageInput, manager: DialogManager):
        try:
            input_money = int(message.text)
            manager.dialog_data["input_money_adding"] = input_money

            await manager.switch_to(BalanceGroup.accept_request)
        except ValueError:
            await message.answer(
                text="<b>🔴 Помилка у введенні</b>\n"
                     "<i>Ви ввели суму не коректно.</i> Будь ласка, дотримуйтеся прикладів: 100, 200, 230, 300 тощо.",
                parse_mode="HTML"
            )

    @staticmethod
    async def accept_deposit(callback: CallbackQuery, button: Button, manager: DialogManager):
        cur_state = manager.dialog_data.get("cur_state")

        is_executor = True if cur_state == ExecutorDialog.executor_state else False

        await callback.answer(
            text="Зараз буде створена платіжка для оформлення платежу"
        )
        try:
            payment_response = await get_invoice_payment_link(
                header_info=HeaderInfo(
                    x_token=X_TOKEN
                ),
                body_info=BodyInfo(
                    amount=int(manager.dialog_data.get("input_money_adding")) * 100,
                    webhook_url=f"{WEBHOOK_URL}/webhook/monobank/{callback.from_user.id}",
                    # redirect_url=TG_GROUP_NAME
                )
            )
        except ValueError as err:
            await manager.done()
            await callback.message.answer("Виникла помилка при створені платежу! Спробуйте пізніше!")
            return

        invoice_id = payment_response.get("invoiceId")
        page_url = payment_response.get("pageUrl")

        await callback.message.answer(
            text=redirect_payment_url,
            reply_markup=create_payment_msg(
                payment_url=page_url
            ),
            parse_mode="HTML"
        )

        response = await Transactions().save_transaction_data(
            invoice_id=invoice_id,
            receiver_id=callback.from_user.id,
            transaction_type=TransactionType.debit,
            transaction_status=TransactionStatus.pending,
            amount=manager.dialog_data.get("input_money_adding"),
        ).do_request()

        if response.is_error:
            await callback.message.answer("Виникла помилка при створенні транзакції! Спробуйте пізніше!")
            return

        await manager.done()
        await callback.message.answer(
            text="При успішній оплаті усі кошти будуть автоматично додані на рахунок!",
            reply_markup=create_keyboard_executor() if is_executor else create_keyboard_client()
        )

    @staticmethod
    async def check_password(message: Message, input_widget: MessageInput, manager: DialogManager):
        password = message.text

        user: UserResponse = await Users().get_user_from_db(telegram_id=message.from_user.id).do_request()

        manager.dialog_data["dialog_user"] = user.model_dump(mode="json")
        is_authorized = user.check_password(
            password=password
        )
        if is_authorized:

            balance: BalanceModel = await Balance().get_user_balance(user_id=user.telegram_id).do_request()
            manager.dialog_data["cards"] = balance.user_cards
            manager.dialog_data["balance"] = balance.balance_money

            await message.answer(
                text="<b>🟢 Пароль підтверджено</b>\n"
                     "<i>Ви успішно ввели пароль.</i> Можете продовжити роботу з ботом.",
                parse_mode="HTML"
            )
            await manager.switch_to(WithdrawingMoneySub.withdraw_sum)
        else:
            await message.answer(
                text="<b>🔴 Помилка</b>\n"
                     "<i>Введений вами пароль неправильний.</i> "
                     "Будь ласка, спробуйте знову або використайте опцію відновлення пароля.",
                parse_mode="HTML"
            )

    @staticmethod
    async def cancel_balance_dialog(callback: CallbackQuery, button: Button, manager: DialogManager):
        cur_state = manager.dialog_data.get("cur_state")
        is_executor = True if cur_state == ExecutorDialog.executor_state else False

        await manager.done(result={"has_ended": True})
        await callback.message.answer(
            text="Завершуємо роботу з балансом",
            reply_markup=create_keyboard_executor() if is_executor else create_keyboard_client()
        )

    @staticmethod
    async def cancel_subdialog(callback: CallbackQuery, button: Button, manager: DialogManager):
        cur_state = manager.dialog_data.get("cur_state")
        is_executor = True if cur_state == ExecutorDialog.executor_state else False
        await manager.done(result={"has_ended": True})
        await callback.message.answer(
            text="Відмінено",
            reply_markup=create_keyboard_executor() if is_executor else create_keyboard_client()
        )


class WithdrawCallbacks:
    @staticmethod
    async def withdraw_all_money(callback: CallbackQuery, button: Button, manager: DialogManager):
        balance = manager.dialog_data.get("balance")
        amount = decimal.Decimal(balance)
        commission_sum = amount * COMMISSION

        manager.dialog_data["input_sum"] = float(round(amount - commission_sum, 2))
        manager.dialog_data["commission_sum"] = float(round(commission_sum, 2))
        await manager.next()

    @staticmethod
    async def process_sum_input(message: Message, input_widget: MessageInput, manager: DialogManager):
        try:
            input_sum = message.text
            input_sum = decimal.Decimal(input_sum)

            if input_sum > manager.dialog_data.get("balance"):
                await message.answer(
                    text="<b>🔴 Недостатній баланс</b>\n"
                         "<i>На вашому рахунку недостатньо коштів.</i> "
                         "Будь ласка, поповніть свій баланс або зменште запитану суму.",
                    parse_mode="HTML"
                )
            elif input_sum <= 0:
                await message.answer(
                    text="<b>🔴 Некоректне значення</b>\n"
                         "<i>Введене вами значення не може бути рівним або меншим за нуль."
                         "</i> Будь ласка, введіть інше значення.",
                    parse_mode="HTML"
                )
            else:
                commission_sum = input_sum * COMMISSION
                manager.dialog_data["input_sum"] = float(round(input_sum - commission_sum, 2))
                manager.dialog_data["commission_sum"] = float(round(commission_sum, 2))
                await manager.switch_to(WithdrawingMoneySub.handle_cards)
        except ValueError:
            await message.answer(
                text="<b>🔴 Помилка у форматі суми</b>\n"
                     "<i>Введена вами сума не відповідає вірному формату.</i> Будь ласка, введіть суму знову.",
                parse_mode="HTML"
            )

    @staticmethod
    async def process_card_input(message: Message, input_widget: MessageInput, manager: DialogManager):
        card_number = message.text.replace(" ", "").strip()
        card_valid = is_valid_card(card_number)

        if card_valid:

            is_updated = await Balance().update_user_cards(
                user_id=message.from_user.id,
                card=card_number
            ).do_request()

            if is_updated.is_error:
                await message.answer(
                    text="Сталася помилка при зберіганні картки!"
                )
                return
            manager.dialog_data["withdrawal_card"] = format_card_number(card_number)
            await manager.switch_to(WithdrawingMoneySub.accept_withdraw)

        else:
            await message.answer(
                text="<b>🔴 Помилка у даних картки</b>\n"
                     "<i>Введене вами значення картки не коректно.</i>"
                     "Будь ласка, перевірте дані та спробуйте ввести знову.",
                parse_mode="HTML"
            )

    @staticmethod
    async def accept_withdraw(callback: CallbackQuery, button: Button, manager: DialogManager):
        cur_state = manager.dialog_data.get("cur_state")
        input_sum = decimal.Decimal(manager.dialog_data.get("input_sum"))
        commission = decimal.Decimal(manager.dialog_data.get("commission_sum"))
        card_number = manager.dialog_data.get("withdrawal_card")

        commission = round(commission, 2)
        input_sum = round(input_sum, 2)

        is_executor = True if cur_state == ExecutorDialog.executor_state else False

        balance_withdrawal = await Balance().perform_fund_transfer(
            user_id=callback.from_user.id,
            amount=round(input_sum + commission, 2),
            action=BalanceAction.withdrawal
        ).do_request()

        if balance_withdrawal.is_error:
            await callback.answer(text='Виникли проблеми з перенесенням коштів! Спробуйте пізніше!')
            await manager.done()
            return

        withdrawal = await Withdrawals().save_withdrawal_data(
            user_id=callback.from_user.id,
            status=WithdrawalStatus.pending,
            amount=input_sum,
            commission=commission,
            payment_method=card_number
        ).do_request()

        if withdrawal.is_error:
            await callback.answer(text='Виникли проблеми з створення запиту на кошти! Спробуйте пізніше!')
            await manager.done()
            await Balance().perform_fund_transfer(
                user_id=callback.from_user.id,
                amount=round(input_sum + commission, 2),
                action=BalanceAction.replenishment
            ).do_request()
            return

        await callback.message.answer(
            text="Скоро кошти з'являться на вашому рахунку!",
            reply_markup=create_keyboard_executor() if is_executor else create_keyboard_client()
        )
        await manager.done()

