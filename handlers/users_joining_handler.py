import os
import random

from aiogram.filters.command import Command, CommandObject
from aiogram import F, Bot
from aiogram.types import Message

from aiogram.enums import DiceEmoji
from aiogram.methods.send_dice import SendDice

from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, JOIN_TRANSITION, ChatMemberUpdated
from aiogram.enums import ChatType
from aiogram.dispatcher.router import Router

from handlers_chatbot.utils.redis_interaction import is_session_active

from dotenv import load_dotenv

from utils.redis_utils import compare_notification_time, set_notification_time

from database.crud import get_chat_object, update_chat_status

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

joining_users_router = Router()

joining_users_router.message.filter(F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}))


@joining_users_router.chat_member(
    ChatMemberUpdatedFilter(JOIN_TRANSITION)
)
async def promote_executor_to_admin(event: ChatMemberUpdated):
    db_chat_id = event.chat.title.split("№")[-1]

    chat_obj = await get_chat_object(
        db_chat_id=int(db_chat_id)
    )

    if event.chat.type == ChatType.SUPERGROUP and chat_obj.chat_type == ChatType.GROUP:
        await update_chat_status(
            db_chat_id=chat_obj.id,
            chat_type=ChatType.SUPERGROUP,
            supergroup_id=event.chat.id
        )


@joining_users_router.message(F.text)
async def check_for_new_messages(message: Message, bot: Bot):
    # TODO: Add time limiting
    print("We are now handling new message from executor")
    db_chat_id = message.chat.title.split("№")[-1]

    chat_obj = await get_chat_object(db_chat_id=int(db_chat_id))

    session_key = f"session:{chat_obj.client_id}:{chat_obj.id}"

    is_active = await is_session_active(
        session_key
    )

    if message.from_user.id == chat_obj.executor_id and not is_active:
        print("Checking for new messages")

        is_delayed = await compare_notification_time(
            int(db_chat_id),
            compare_time=5
        )
        print("Getting delay data")

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


@joining_users_router.message(
    Command("cum_on_my_face")
)
async def cum_on_my_face(message: Message):
    await message.answer(
        text="Special command for Vanya!\n\nIf your are a random user - Have a nice cum today!"
    )

    await message.bot(
        SendDice(
            chat_id=message.chat.id,
            emoji=random.choice([DiceEmoji.DICE, DiceEmoji.DART, DiceEmoji.BOWLING, DiceEmoji.SLOT_MACHINE])
        )
    )


@joining_users_router.message(
    Command("vika")
)
async def get_vika_message(message: Message, command: CommandObject):
    text = command.args

    if text:
        await message.answer(
            text=f"Користувач з ніком @{message.from_user.username} висрав повну дічь\n\n"
                 f"Найкраща порада перевіритсь в психолога!\n\n"
                 f"Ще й ось таке написав: <i>{text}</i>",
            parse_mode="HTML"
        )
    else:
        await message.answer(
            text=f"Користувач з ніком @{message.from_user.username} висрав повну дічь\n\n"
                 f"Найкраща порада перевіритсь в психолога!\n\n"
        )

    await message.answer(
        text="( ͡• ͜ʖ ͡•)"
             "( ͡• ͜ʖ ͡•)"
             "( ͡• ͜ʖ ͡•)"
             "( ͡• ͜ʖ ͡•)"
             "( ͡• ͜ʖ ͡•)"
    )
