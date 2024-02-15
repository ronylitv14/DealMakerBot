import decimal

from aiogram import Bot
from aiogram.types import CallbackQuery

from database_api.components.payments import Payments
from database_api.components.tasks import TaskModel, Tasks, PropositionBy, TaskStatus
from handlers_chatbot.utils.sending_review_proposal import send_review_proposal_to_participants
from utils.channel_creating import send_bot_message, edit_telegram_message


async def accept_success_execution(
        bot: Bot,
        callback: CallbackQuery,
        transaction_id: int,
        task_id: int,
        receiver_id: int,
        amount: str,

):
    payment = await Payments().accept_offer(
        transaction_id=transaction_id,
        task_id=task_id,
        receiver_id=receiver_id,
    ).do_request()

    if payment.is_error:
        return await callback.answer("Неможливо зараз обробити цей запит! Можливо у вас не вистачає коштів!")

    await callback.answer()

    rounded_amount = round(decimal.Decimal(amount), 2)

    await send_bot_message(
        user_id=receiver_id,
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
