import os
import sys
from pydantic import BaseModel
from copy import copy

from aiogram import types, Bot
from aiogram.methods import DeleteMessage
from aiogram.types import ContentType

from telethon import TelegramClient
from telethon import functions

from keyboards.inline_keyboards import create_group_message_keyboard_telethon
from telethon.types import Updates, ChatBannedRights

from utils.redis_utils import deactivate_session, store_message_in_redis, construct_session_key
from utils.dialog_texts import greetings_text

from database_api.components.tasks import TaskStatus
from database_api.components.group_messages import GroupMessages, GroupMessageResponse
from database_api.components.chats import Chats, ChatModel

from dotenv import load_dotenv

load_dotenv()

ADMIN_SESSIONS_DIR = os.getenv("ADMIN_SESSIONS_DIR")
TELEGRAM_USER = [os.path.join(ADMIN_SESSIONS_DIR, i) for i in os.listdir(ADMIN_SESSIONS_DIR)]
TELEGRAM_APP_API_ID = int(os.getenv("TELEGRAM_APP_API_ID"))
TELEGRAM_APP_API_HASH = os.getenv("TELEGRAM_APP_API_HASH")

BOT_TOKEN = os.getenv("BOT_TOKEN")

BOT_URL = os.getenv("BOT_URL")
CHAT_BOT_URL = os.getenv("CHAT_BOT_URL")

TG_GROUPNAME = os.getenv("TG_GROUP_NAME")

if not all((TELEGRAM_USER, TELEGRAM_APP_API_ID, TELEGRAM_APP_API_HASH)):
    print("Did not specify TELETHON params")
    sys.exit(1)


class AdminRights:
    def __init__(
            self,
            change_info=False,
            post_messages=False,
            edit_messages=False,
            delete_messages=False,
            ban_users=False,
            invite_users=False,
            pin_messages=False,
            add_admins=False,
            manage_call=False,
            anonymous=False,
            is_admin=False,
            title=""
    ):
        params = locals()
        params.pop('self')

        self.params = params

        self.change_info = change_info
        self.post_messages = post_messages
        self.edit_messages = edit_messages
        self.delete_messages = delete_messages
        self.ban_users = ban_users
        self.invite_users = invite_users
        self.pin_messages = pin_messages
        self.add_admins = add_admins
        self.manage_call = manage_call
        self.anonymous = anonymous
        self.is_admin = is_admin
        self.title = title

    def get_user_rights(self):
        return {name: value for name, value in self.params.items()}


MSG_STATUS_EMOJI = {
    TaskStatus.executing: "🟠",
    TaskStatus.done: "🔴"
}


async def create_new_message_text(task_id: int, new_status: TaskStatus):
    # group_msg: GroupMessage = await get_group_message(task_id)
    group_msg: GroupMessageResponse = await GroupMessages().get_group_message_by_task(task_id).do_request()
    edited_msg = "#" + group_msg.message_text.split(sep="#", maxsplit=1)[1]
    edited_msg = f"{MSG_STATUS_EMOJI[new_status]} {new_status.value}\n\n" + edited_msg

    return edited_msg, group_msg.group_message_id, group_msg.has_files


async def create_channel_with_users(chname: str, chat_admin: str, task_id: int, *users):
    chat_admin_copy = copy(chat_admin)

    admins_sessions = set(TELEGRAM_USER.copy())
    admins_sessions.discard(chat_admin_copy)

    admins_sessions = iter(admins_sessions)

    while admins_sessions:
        try:
            async with TelegramClient(chat_admin_copy, TELEGRAM_APP_API_ID, TELEGRAM_APP_API_HASH) as client:

                result: Updates = await client(
                    functions.messages.CreateChatRequest(
                        title=chname,
                        users=list(users)
                    )
                )

                await client(functions.messages.EditChatDefaultBannedRightsRequest(
                    peer=result.chats[0].id,
                    banned_rights=ChatBannedRights(
                        change_info=True,
                        until_date=None,
                        invite_users=True,
                        send_games=True
                    )
                ))

                await client(functions.messages.EditChatAboutRequest(
                        peer=result.chats[0].id,
                        about=f"Номер замовлення №{task_id}"
                    )
                )

                return result.chats[0].id, chat_admin_copy
        except Exception as err:
            try:
                chat_admin_copy = next(admins_sessions)
            except StopIteration:
                print("All admin sessions tried and failed.")
                break


async def change_chat_title(
        chat_title: str,
        chat_id: int,
        chat_admin: str = "admin",
        chat_desc: str = ""
):
    async with TelegramClient(chat_admin, TELEGRAM_APP_API_ID, TELEGRAM_APP_API_HASH) as client:
        await client(
            functions.messages.EditChatTitleRequest(
                chat_id=chat_id,
                title=chat_title
            )
        )
        if chat_desc:
            await client(
                functions.messages.EditChatAboutRequest(
                    peer=chat_id,
                    about=chat_desc,
                )
            )


async def add_admin_rights(
        chat_id: int,
        user: str,
        user_rights: AdminRights = None,
        admin_name: str = "admin",
        change_info: bool = None, post_messages: bool = None, edit_messages: bool = None, delete_messages: bool = None,
        ban_users: bool = None, invite_users: bool = None, pin_messages: bool = None, add_admins: bool = None,
        manage_call: bool = None, anonymous: bool = None, is_admin: bool = None, title: str = None
):
    async with TelegramClient(admin_name, TELEGRAM_APP_API_ID, TELEGRAM_APP_API_HASH) as client:
        if user_rights:
            await client.edit_admin(
                chat_id,
                user,
                **user_rights.get_user_rights()
            )

            return

        await client.edit_admin(
            chat_id,
            user,
            change_info=change_info,
            post_messages=post_messages,
            edit_messages=edit_messages,
            delete_messages=delete_messages,
            ban_users=ban_users,
            invite_users=invite_users,
            pin_messages=pin_messages,
            add_admins=add_admins,
            manage_call=manage_call,
            anonymous=anonymous,
            is_admin=is_admin,
            title=title
        )


async def get_chat_invite_link(chat_id: int, admin_name: str):
    async with TelegramClient(admin_name, TELEGRAM_APP_API_ID, TELEGRAM_APP_API_HASH) as client:
        link = await client(
            functions.messages.ExportChatInviteRequest(
                peer=chat_id,
                legacy_revoke_permanent=True,
                request_needed=False
            )
        )

        return link.link


async def edit_telegram_message(task_id: int, is_active: bool, new_status: TaskStatus):
    async with TelegramClient('bot_deals', TELEGRAM_APP_API_ID, TELEGRAM_APP_API_HASH) as bot:
        new_text, message_id, has_files = await create_new_message_text(task_id=task_id, new_status=new_status)
        reply_markup = create_group_message_keyboard_telethon(
            task_id=task_id,
            has_files=has_files,
            is_active=is_active
        )

        await bot(
            functions.messages.EditMessageRequest(
                peer=TG_GROUPNAME,
                message=new_text,
                id=message_id,
                reply_markup=reply_markup if reply_markup.rows else None
            )
        )


async def send_bot_message(msg: str, user_id: int, bot_session: str = "bot_deals", reply_markup=None):
    async with TelegramClient(bot_session, TELEGRAM_APP_API_ID, TELEGRAM_APP_API_HASH) as bot:
        await bot.send_message(
            user_id,
            msg,
            parse_mode="HTML",
            buttons=reply_markup
        )


async def send_bot_single_inline_message(
        chat_id: int,
        msg_text: str,
        url: str,
        bot: Bot,
        btn_text: str = "Перейти до чату",
):
    await bot.send_message(
        chat_id=chat_id,
        text=msg_text,
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text=btn_text,
                        url=url
                    )
                ]
            ]
        ),
        parse_mode="HTML"
    )


class CustomMessage(BaseModel):
    content_type: ContentType
    text: str


async def send_instructions_to_chat(client_id: int, db_chat_id: int):
    instructions_msg = CustomMessage(
        content_type=ContentType.TEXT,
        text=greetings_text
    )

    await store_message_in_redis(
        construct_session_key(client_id, db_chat_id=db_chat_id),
        instructions_msg
    )


async def creating_chat_for_users(task_id: int, chat_admin: str, executor_id: int, client_id: int, callback, bot,
                                  desc_client: str = "", desc_executor: str = ""):
    group_name = f"Замовлення №{task_id}"

    chat_id, chat_admin = await create_channel_with_users(
        group_name,
        chat_admin,
        task_id,
        BOT_URL,
        CHAT_BOT_URL
    )

    await add_admin_rights(
        chat_id=chat_id,
        user=BOT_URL,
        is_admin=True,
        admin_name=chat_admin,
    )

    await add_admin_rights(
        chat_id=chat_id,
        user=CHAT_BOT_URL,
        is_admin=True,
        admin_name=chat_admin,
        title="Клієнт"
    )

    link = await get_chat_invite_link(chat_id=chat_id, admin_name=chat_admin)

    new_chat: ChatModel = await Chats().save_chat_data(
        chat_id=chat_id,
        invite_link=link,
        participants_count=4,
        group_name=group_name,
        task_id=task_id,
        executor_id=executor_id,
        client_id=client_id,
        chat_admin=chat_admin
    ).do_request()

    if not isinstance(new_chat, ChatModel):
        return await callback.answer("Помилка при створенні чату!")

    await change_chat_title(
        chat_id=new_chat.chat_id,
        chat_admin=chat_admin,
        chat_title=f"Угода №{new_chat.id}"
    )

    await deactivate_session(
        session_key=f"session:{new_chat.client_id}:{new_chat.id}"
    )

    msg_text_client = "За цим посиланням ви можете перейти до діалогу з виконавцем" if not desc_client else desc_client

    await send_instructions_to_chat(
        client_id=client_id,
        db_chat_id=new_chat.id,
    )

    await send_bot_single_inline_message(
        chat_id=client_id,
        msg_text=msg_text_client,
        btn_text="Перейти до чату",
        url=f"{CHAT_BOT_URL}?start=chat-{new_chat.id}",
        bot=bot
    )

    await send_bot_single_inline_message(
        chat_id=executor_id,
        msg_text="За цим посиланням ви можете перейти до діалогу з клієнтом" if not desc_executor else desc_executor,
        btn_text="Перейти до чату",
        url=link,
        bot=bot
    )

    await callback.answer()

    await bot(
        DeleteMessage(
            message_id=int(callback.message.message_id),
            chat_id=callback.message.chat.id
        )
    )

    await Chats().update_group_title(
        db_chat_id=new_chat.id,
        group_name=f"Угода №{new_chat.id}"
    ).do_request()
