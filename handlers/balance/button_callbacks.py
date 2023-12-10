import decimal
import os

from aiogram.types import CallbackQuery, Message
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.dialog import DialogManager

from handlers.states_handler import ExecutorDialog, ClientDialog
from .window_state import BalanceGroup, WithdrawingMoneySub
from keyboards.inline_keyboards import create_payment_msg
from keyboards.clients import create_keyboard_client
from keyboards.executors import create_keyboard_executor
from utils.dialog_texts import redirect_payment_url
from utils.bank_card_utils import is_valid_card
from handlers.utils.payment_system import BodyInfo, HeaderInfo, get_invoice_payment_link
from database.crud import get_user_auth, get_user_balance, update_user_cards, add_transaction_data, create_withdrawal_request
from database.models import User, TransactionType, TransactionStatus, WithdrawalStatus

from dotenv import load_dotenv

load_dotenv()

X_TOKEN = os.getenv("X_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
COMMISSION = decimal.Decimal("0.03")

class ButtonCallbacks:
    @staticmethod
    async def add_money(callback: CallbackQuery, button: Button, manager: DialogManager):
        await manager.switch_to(BalanceGroup.adding_money)

    @staticmethod
    async def process_money_adding(message: Message, input_widget: MessageInput, manager: DialogManager):
        try:
            input_money = int(message.text)
            manager.dialog_data["money"] = input_money
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

        payment_response = await get_invoice_payment_link(
            header_info=HeaderInfo(
                x_token=X_TOKEN
            ),
            body_info=BodyInfo(
                amount=int(manager.dialog_data.get("money")) * 100,
                webhook_url=f"{WEBHOOK_URL}/{callback.from_user.id}",
                redirect_url="https://t.me/newdopomogatestbot"
            )
        )

        invoice_id = payment_response.get("invoiceId")
        page_url = payment_response.get("pageUrl")

        await callback.message.answer(
            text=redirect_payment_url,
            reply_markup=create_payment_msg(
                payment_url=page_url
            ),
            parse_mode="HTML"
        )

        await add_transaction_data(
            invoice_id=invoice_id,
            receiver_id=callback.from_user.id,
            transaction_type=TransactionType.debit,
            transaction_status=TransactionStatus.pending,
            amount=manager.dialog_data.get("money"),
        )

        await manager.done()
        await callback.message.answer(
            text="При успішній оплаті усі кошти будуть автоматично додані на рахунок!",
            reply_markup=create_keyboard_executor() if is_executor else create_keyboard_client()
        )

    @staticmethod
    async def accept_withdraw(callback: CallbackQuery, button: Button, manager: DialogManager):
        cur_state = manager.dialog_data.get("cur_state")
        input_sum = decimal.Decimal(manager.dialog_data.get("input_sum"))
        card_number = manager.dialog_data.get("withdrawal_card")

        commission = decimal.Decimal(input_sum) * COMMISSION

        is_executor = True if cur_state == ExecutorDialog.executor_state else False

        await create_withdrawal_request(
            user_id=callback.from_user.id,
            status=WithdrawalStatus.pending,
            amount=input_sum - commission,
            commission=commission,
            payment_method=card_number
        )

        await callback.message.answer(
            text="Скоро кошти з'являться на вашому рахунку!",
            reply_markup=create_keyboard_executor() if is_executor else create_keyboard_client()
        )
        await manager.done(result={"has_ended": True})

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

    @staticmethod
    async def check_password(message: Message, input_widget: MessageInput, manager: DialogManager):
        password = message.text
        user: User = await get_user_auth(
            telegram_id=message.from_user.id
        )
        manager.dialog_data["dialog_user"]: User = user
        is_authorized = user.check_password(
            password=password
        )
        if is_authorized:

            balance = await get_user_balance(user_id=user.telegram_id)
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
    async def process_sum_input(message: Message, input_widget: MessageInput, manager: DialogManager):
        try:
            input_sum = message.text
            input_sum = float(input_sum)

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
                manager.dialog_data["input_sum"] = input_sum
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
            is_updated = await update_user_cards(
                user_id=message.from_user.id,
                card=card_number
            )

            if not is_updated:
                await message.answer(
                    text="Сталася помилка при зберіганні картки!"
                )
                return
            manager.dialog_data["withdrawal_card"] = card_number
            await manager.switch_to(WithdrawingMoneySub.accept_withdraw)

        else:
            await message.answer(
                text="<b>🔴 Помилка у даних картки</b>\n"
                     "<i>Введене вами значення картки не коректно.</i>"
                     "Будь ласка, перевірте дані та спробуйте ввести знову.",
                parse_mode="HTML"
            )
