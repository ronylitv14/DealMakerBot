import asyncio
import os
import sys

from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from dotenv import load_dotenv

from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import types
from aiogram_dialog import setup_dialogs
from handlers.users_joining_handler import joining_users_router
from handlers.auth_handler import auth_router
from handlers_chatbot.start_handler import main_router

from handlers import main_handlers

load_dotenv("./.env")

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_BOT_TOKEN = os.getenv("CHAT_BOT_TOKEN")

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

REDIS_DEAL_DB = os.getenv("REDIS_DB")
REDIS_CHAT_DB = os.getenv("REDIS_CHAT_DB")

if not BOT_TOKEN:
    print("`BOT_TOKEN` was not specified!")
    sys.exit(1)


async def main():
    # memory_storage = MemoryStorage()

    redis_url_deal = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DEAL_DB}"
    redis_url_chat = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_CHAT_DB}"
    if REDIS_PASSWORD:
        redis_url_deal = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DEAL_DB}"
        redis_url_chat = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_CHAT_DB}"

    deal_storage = RedisStorage.from_url(
        url=redis_url_deal,
        key_builder=DefaultKeyBuilder(with_destiny=True),
    )
    chat_storage = RedisStorage.from_url(url=redis_url_chat, key_builder=DefaultKeyBuilder(with_destiny=True))

    dp = Dispatcher(storage=deal_storage)
    dp_chat = Dispatcher(storage=chat_storage)

    bot = Bot(token=BOT_TOKEN)
    chat_bot = Bot(token=CHAT_BOT_TOKEN)

    types_command = [
        types.BotCommand(command="menu", description="Відкрити меню команд"),
        types.BotCommand(command="ticket", description="Створити тікет")
    ]

    chat_types_command = [
        types.BotCommand(command="get_chat", description="Отримати меню з усіма чатами"),
        types.BotCommand(command="pay", description="Оплата замовлення")
    ]

    dp.include_routers(
        main_handlers.main_router,
        auth_router,
        joining_users_router
    )

    dp_chat.include_routers(
        main_router
    )

    setup_dialogs(dp)
    setup_dialogs(dp_chat)

    await bot.set_my_commands(types_command)
    await chat_bot.set_my_commands(chat_types_command)
    await asyncio.gather(
        dp.start_polling(bot),
        dp_chat.start_polling(chat_bot),
        bot.delete_webhook(),
        chat_bot.delete_webhook()
    )


if __name__ == '__main__':
    asyncio.run(main())
