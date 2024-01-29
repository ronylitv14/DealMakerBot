import decimal

from aiogram import Bot

from database_api.components.tasks import TaskModel, Tasks
from database_api.components.users import Users, UserResponse
from utils.channel_creating import send_bot_message
from keyboards.inline_keyboards import create_review_reply_markup, create_accept_offer_msg
from utils.dialog_texts import start_review_text


async def send_accept_offer_msg(
        bot: Bot,
        task_id: int,
        transaction_id: int,
        amount: decimal.Decimal,
        receiver_id: int,
        chat_id: int,
        deal_chat: int
):
    task: TaskModel = await Tasks().get_task_data(task_id).do_request()

    task_msg = f"Номер чату {deal_chat}\n" + task.create_task_summary()

    await bot.send_message(
        chat_id=chat_id,
        text=f"{task_msg}\n\nДане повідомлення призначення для того, щоб підтвердити успішне виконання завдання виконавцем."
             " Зараз гроші знаходяться на утриманні, з Вашого балансу вони зняті, але ще не перераховані виконавцю! "
             "При будь-яких проблемах звертайтеся до адміна або пишіть тікет за командою /ticket",
        reply_markup=create_accept_offer_msg(
            task_id=task_id,
            transaction_id=transaction_id,
            receiver_id=receiver_id,
            amount=amount
        )
    )


async def send_review_proposal_to_participants(
        task_id: int,
        executor_id: int,
        client_id: int
):

    client: UserResponse = await Users().get_user_from_db(client_id).do_request()
    executor: UserResponse = await Users().get_user_from_db(executor_id).do_request()

    await send_bot_message(
        msg=start_review_text.format(username=executor.username, task_id=task_id),
        user_id=client_id,
        reply_markup=create_review_reply_markup(
            reviewer_id=client_id,
            reviewed_id=executor_id,
            task_id=task_id
        )
    )

    await send_bot_message(
        msg=start_review_text.format(username=client.username, task_id=task_id),
        user_id=executor_id,
        reply_markup=create_review_reply_markup(
            reviewer_id=executor_id,
            reviewed_id=client_id,
            task_id=task_id
        )
    )
