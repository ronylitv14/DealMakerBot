import os
from dotenv import load_dotenv

from aiogram import F, Bot
from aiogram.types import Message
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, JOIN_TRANSITION, ChatMemberUpdated
from aiogram.enums import ChatType
from aiogram.dispatcher.router import Router

from utils.dialog_texts import greetings_text
from utils.redis_utils import compare_notification_time, set_notification_time, is_session_active
from database_api.components.chats import Chats, ChatModel

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

joining_users_router = Router()

joining_users_router.message.filter(F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}))


@joining_users_router.chat_member(
    ChatMemberUpdatedFilter(JOIN_TRANSITION)
)
async def promote_executor_to_admin(event: ChatMemberUpdated):
    if event.chat.type == ChatType.CHANNEL:
        return
    db_chat_id = event.chat.title.split("№")[-1]

    chat_obj: ChatModel = await Chats().get_chat_data(db_chat_id=int(db_chat_id)).do_request()

    if event.chat.type == ChatType.SUPERGROUP and chat_obj.chat_type == ChatType.GROUP:
        await Chats().update_chat_type(
            db_chat_id=chat_obj.id,
            chat_type=ChatType.SUPERGROUP,
            supergroup_id=event.chat.id
        ).do_request()


@joining_users_router.message(F.text)
async def check_for_new_messages(message: Message, bot: Bot):
    # TODO: Add time limiting
    print("We are now handling new message from executor")
    db_chat_id = message.chat.title.split("№")[-1]

    chat_obj: ChatModel = await Chats().get_chat_data(db_chat_id=int(db_chat_id)).do_request()

    session_key = f"session:{chat_obj.client_id}:{chat_obj.id}"

    is_active = await is_session_active(
        session_key
    )

    if message.from_user.id == chat_obj.executor_id and not is_active:

        is_delayed = await compare_notification_time(
            int(db_chat_id),
            compare_time=5
        )

        if is_delayed:
            print("Inside sending notifications!")
            await bot.send_message(
                chat_id=chat_obj.client_id,
                text=f"<b>Вам прийшло нове повідомлення, щодо {chat_obj.group_name}!</b>\n\n"
                     f"Перейдіть до чату через кнопку '<i>Мої замовлення</i>'",
                parse_mode="HTML"
            )

            await set_notification_time(
                int(db_chat_id)
            )
