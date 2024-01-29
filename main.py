import asyncio
import os
import sys

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
# REDIS_URL = os.getenv("REDIS_URL")

if not BOT_TOKEN:
    print("`BOT_TOKEN` was not specified!")
    sys.exit(1)


async def main():
    memory_storage = MemoryStorage()

    dp = Dispatcher(storage=memory_storage)
    dp_chat = Dispatcher(storage=memory_storage)

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
        dp_chat.start_polling(chat_bot)
    )


if __name__ == '__main__':
    asyncio.run(main())
