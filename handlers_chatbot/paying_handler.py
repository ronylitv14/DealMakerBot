import decimal

from aiogram import F, types, Bot
from aiogram.enums import ChatType
from aiogram.filters.command import Command
from aiogram.dispatcher.router import Router
from aiogram_dialog.dialog import DialogManager
from aiogram_dialog.api.entities import StartMode

from handlers_chatbot.paying_order.window_dialogs import create_offer_dialog
from handlers_chatbot.paying_order.window_states import PriceOffer
from handlers_chatbot.utils.sending_review_proposal import send_review_proposal_to_participants

from keyboards.inline_keyboards import send_accept_offer_msg

from utils.channel_creating import edit_telegram_message, send_bot_message

from database_api.components.chats import Chats, ChatModel
from database_api.components.tasks import Tasks, TaskStatus, TaskModel, PropositionBy
from database_api.components.transactions import TransactionModel
from database_api.components.payments import Payments, SuccessModel

paying_router = Router()

paying_router.message.filter(F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP, ChatType.PRIVATE}))
paying_router.include_routers(*create_offer_dialog())


@paying_router.message(
    Command("pay")
)
async def create_payment(message: types.Message, dialog_manager: DialogManager):
    if message.chat.type == ChatType.PRIVATE:
        return await message.answer("Ціну може пропонувати тільки виконавець!")
    chat_db_id = message.chat.title.split("№")[-1]

    chat_obj: ChatModel = await Chats().get_chat_data(db_chat_id=int(chat_db_id)).do_request()
    task: TaskModel = await Tasks().get_task_data(chat_obj.task_id).do_request()

    is_payed: SuccessModel = await Payments().check_payment_status(
        task_id=chat_obj.task_id,
        sender_id=chat_obj.client_id,
        receiver_id=chat_obj.executor_id
    ).do_request()

    if isinstance(is_payed, SuccessModel) and is_payed.status:
        return await message.answer("Це завдання оплачено! Щоб здійснити оплату ще раз зробіть нове замовлення!")

    if task.executor_id is not None and task.proposed_by == PropositionBy.public:
        return await message.answer("Це завдання вже виконується іншим виконавцем!")

    await dialog_manager.start(
        state=PriceOffer.offer_price,
        mode=StartMode.RESET_STACK,
        data={
            "chat_obj": chat_obj.model_dump(mode="json")
        }
    )


@paying_router.callback_query(
    F.data.startswith("offer")
)
async def process_offer(callback: types.CallbackQuery, bot: Bot):
    action, chat_id, task_id, price = callback.data.split("|")

    chat: ChatModel = await Chats().get_chat_data(db_chat_id=int(chat_id)).do_request()

    transaction = await Payments().perform_money_transfer(
        receiver_id=chat.executor_id,
        sender_id=chat.client_id,
        amount=decimal.Decimal(price),
        task_id=int(task_id)
    ).do_request()

    if not isinstance(transaction, TransactionModel):
        match transaction.status_code:
            case 400:
                await callback.message.answer(text="У вас недостатньо коштів! Поповніть баланс та спробуйте ще раз!")
                await callback.answer()
            case _:
                await callback.answer(text="Неможливо зараз здійснити транзакцію!")
        return

    await callback.answer()

    await bot.delete_message(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id
    )

    await send_accept_offer_msg(
        bot=bot,
        deal_chat=chat.id,
        task_id=transaction.task_id,
        chat_id=callback.from_user.id,
        receiver_id=transaction.receiver_id,
        transaction_id=transaction.transaction_id,
        amount=transaction.amount
    )

    await bot.send_message(
        chat_id=-chat.chat_id if not chat.supergroup_id else chat.supergroup_id,
        text="<b>Клієнт підтвердив замовлення! Можна розпочинати виконання!</b>",
        parse_mode="HTML"
    )

    task: TaskModel = await Tasks().get_task_data(task_id=chat.task_id).do_request()

    if task.proposed_by == PropositionBy.public:
        await edit_telegram_message(
            task_id=int(task_id),
            new_status=TaskStatus.executing,
            is_active=False
        )


@paying_router.callback_query(
    F.data.startswith("reject")
)
async def process_reject(callback: types.CallbackQuery, bot: Bot):
    action, chat_id, task_id, price = callback.data.split("|")
    print("Reject")

    await bot.send_message(
        chat_id=int(chat_id),
        text="<b>Клієнт відмовився від запропонованої вами ціни!</b>\n\nСпробуйте домовитися знову!",
        parse_mode="HTML"
    )

    await callback.answer()
    await bot.delete_message(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id
    )


@paying_router.callback_query(
    F.data.startswith("accept_offer")
)
async def accept_offer(callback: types.CallbackQuery, bot: Bot):
    action, transaction_id, task_id, amount, receiver_id = callback.data.split("|")

    payment = await Payments().accept_offer(
        transaction_id=int(transaction_id),
        task_id=int(task_id),
        receiver_id=int(receiver_id),
    ).do_request()

    if payment.is_error:
        return await callback.answer("Неможливо зараз обробити цей запит! Можливо у вас не вистачає коштів!")

    await callback.answer()

    rounded_amount = round(decimal.Decimal(amount), 2)

    await send_bot_message(
        user_id=int(receiver_id),
        msg=f"Вам надійшли кошти щодо завдання у розмірі: <b>{rounded_amount}</b> грн",
    )

    await bot.delete_message(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id
    )

    task: TaskModel = await Tasks().get_task_data(int(task_id)).do_request()

    if task.proposed_by == PropositionBy.public:
        await edit_telegram_message(
            task_id=int(task_id),
            new_status=TaskStatus.done,
            is_active=False
        )

    await send_review_proposal_to_participants(
        task_id=task.task_id,
        client_id=task.client_id,
        executor_id=task.executor_id
    )
