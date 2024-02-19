import os

from dotenv import load_dotenv

from aiogram import Bot
from aiogram.types import ChatMemberLeft, ChatMemberBanned, CallbackQuery

from database_api.components.chats import Chats, ChatsList, ChatModel

from utils.channel_creating import send_bot_single_inline_message, change_chat_title
from utils.redis_utils import deactivate_session, construct_session_key

load_dotenv()

CHAT_BOT_URL = os.getenv("CHAT_BOT_URL")


async def check_oldest_unused_chats():
    chats: ChatsList = await Chats().get_all_unused_chats().do_request()

    if not isinstance(chats, ChatsList):
        return []
    return chats


async def delete_user_from_chat(bot: Bot, chat: ChatModel):
    chat_id = -chat.chat_id if not chat.supergroup_id else chat.supergroup_id

    executor = await bot.get_chat_member(
        chat_id=chat_id,
        user_id=chat.executor_id
    )

    if isinstance(executor, ChatMemberLeft) or isinstance(executor, ChatMemberBanned):
        await Chats().update_chat_field(db_chat_id=chat.id, active=False, in_use=False).do_request()
        return True

    await deactivate_session(
        session_key=construct_session_key(client_id=chat.client_id, db_chat_id=chat.id)
    )

    await bot.ban_chat_member(
        chat_id=chat_id,
        user_id=chat.executor_id
    )

    res = await Chats().update_chat_field(db_chat_id=chat.id, active=False, in_use=False).do_request()

    res.raise_for_status()

    return True


async def create_inactive_chat(db_chat_id: int, bot: Bot, admin_id: int):
    chat: ChatModel = await Chats().get_chat_data(db_chat_id=db_chat_id).do_request()

    if not isinstance(chat, ChatModel):
        return await bot.send_message(chat_id=admin_id, text="Неможливо зараз зробити ваш запит!")

    return await delete_user_from_chat(
        bot=bot,
        chat=chat
    )


async def add_new_user_to_chat(chat_model: ChatModel, bot: Bot, task_id: int, client_id: int, executor_id: int):
    chat_id = -chat_model.chat_id if not chat_model.supergroup_id else chat_model.supergroup_id

    new_invite_link = await bot.create_chat_invite_link(
        chat_id=chat_id
    )

    new_chat: ChatModel = await Chats().save_chat_data(
        chat_id=chat_model.chat_id,
        supergroup_id=chat_model.supergroup_id,
        task_id=task_id,
        chat_admin=chat_model.chat_admin,
        client_id=client_id,
        executor_id=executor_id,
        group_name="Нове замовлення",
        invite_link=new_invite_link.invite_link,
        participants_count=chat_model.participants_count
    ).do_request()

    if not isinstance(new_chat, ChatModel):
        raise ValueError()

    chat_title = f"Угода №{new_chat.id}"

    await Chats().update_chat_field(db_chat_id=chat_model.id, in_use=True).do_request()
    await Chats().update_chat_field(db_chat_id=new_chat.id, group_name=chat_title, active=True,
                                    in_use=False).do_request()

    await change_chat_title(
        chat_id=chat_model.chat_id,
        chat_admin=chat_model.chat_admin,
        chat_title=chat_title,
        chat_desc=f"Номер замовлення №{task_id}"
    )

    await send_bot_single_inline_message(
        chat_id=client_id,
        bot=bot,
        msg_text="За цим посиланням ви розпочнете чат з виконавцем",
        url=f"{CHAT_BOT_URL}?start=chat-{new_chat.id}"
    )

    await send_bot_single_inline_message(
        chat_id=executor_id,
        bot=bot,
        msg_text="За цим посиланням ви розпочнете чат з клієнтом",
        url=new_invite_link.invite_link
    )


async def create_used_chat(bot: Bot, client_id: int, task_id: int, executor_id: int):
    chats = await check_oldest_unused_chats()

    if not chats:
        raise ValueError("No avaliable chats at the moment")

    chat: ChatModel = chats[0]

    await delete_user_from_chat(
        bot=bot,
        chat=chat
    )

    await add_new_user_to_chat(
        bot=bot,
        client_id=client_id,
        task_id=task_id,
        executor_id=executor_id,
        chat_model=chat
    )

    return True


async def check_existence_and_create_new_deal(bot: Bot, callback: CallbackQuery, task_id: int, executor_id: int,
                                              client_id: int):
    is_created = await Chats().check_chat_existence(
        task_id=int(task_id),
        executor_id=int(executor_id),
        client_id=int(client_id)
    ).do_request()

    if is_created.is_success:
        await callback.answer()
        return await callback.message.reply(text="Цей чат вже створено!")

    try:
        res = await create_used_chat(
            bot=bot,
            client_id=int(client_id),
            task_id=int(task_id),
            executor_id=int(executor_id)
        )
        if res:
            await bot.delete_message(
                chat_id=callback.from_user.id,
                message_id=callback.message.message_id
            )
            return
    except ValueError as err:
        raise
