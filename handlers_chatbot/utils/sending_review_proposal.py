from database_api.components.users import Users, UserResponse
from utils.channel_creating import send_bot_message
from keyboards.inline_keyboards import create_review_reply_markup
from utils.dialog_texts import start_review_text


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
