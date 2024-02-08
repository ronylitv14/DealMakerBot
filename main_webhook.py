import asyncio
import os
import sys

import logging
from dotenv import load_dotenv

from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder

from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram_dialog import setup_dialogs

from handlers.users_joining_handler import joining_users_router
from handlers.auth_handler import auth_router
from handlers_chatbot.start_handler import main_router

from handlers import main_handlers

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_BOT_TOKEN = os.getenv("CHAT_BOT_TOKEN")

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
REDIS_DEAL_DB = os.getenv("REDIS_DB")
REDIS_CHAT_DB = os.getenv("REDIS_CHAT_DB")

if not BOT_TOKEN or not CHAT_BOT_TOKEN:
    sys.exit("Please provide BOT_TOKEN and CHAT_BOT_TOKEN")

WEB_SERVER_HOST = "0.0.0.0"
WEB_SERVER_PORT_DEAL = 8080
WEB_SERVER_PORT_CHAT = 8082

BASE_WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Bot 1 settings
WEBHOOK_PATH_BOT = "/webhook-bot"
WEBHOOK_SECRET_BOT = os.getenv("WEBHOOK_SECRET_BOT")

# Bot 2 settings
WEBHOOK_PATH_CHATBOT = "/webhook-chatbot"
WEBHOOK_SECRET_CHATBOT = os.getenv("WEBHOOK_SECRET_CHATBOT")


async def on_startup_bot(bot: Bot):
    await bot.set_webhook(f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH_BOT}",
                          secret_token=WEBHOOK_SECRET_BOT, )
    types_command = [
        types.BotCommand(command="menu", description="Створення основного меню"),
        types.BotCommand(command="ticket", description="Стоврення тікету на користувача")
    ]

    await bot.set_my_commands(types_command)


async def on_startup_chatbot(bot: Bot):
    await bot.set_webhook(f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH_CHATBOT}", secret_token=WEBHOOK_SECRET_CHATBOT)

    chat_types_command = [
        types.BotCommand(command="get_chat", description="Почати інший чат"),
        types.BotCommand(command="pay", description="Оплата замовлення")
    ]

    await bot.set_my_commands(chat_types_command)


def main():
    redis_url_deal = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DEAL_DB}"
    redis_url_chat = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_CHAT_DB}"

    if REDIS_PASSWORD:
        redis_url_deal = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DEAL_DB}"
        redis_url_chat = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_CHAT_DB}"

    deal_storage = RedisStorage.from_url(url=redis_url_deal, key_builder=DefaultKeyBuilder(with_destiny=True))
    chat_storage = RedisStorage.from_url(url=redis_url_chat, key_builder=DefaultKeyBuilder(with_destiny=True))

    dp_deal = Dispatcher(storage=deal_storage)
    dp_chatbot = Dispatcher(storage=chat_storage)

    bot_deal = Bot(BOT_TOKEN, parse_mode=ParseMode.HTML)
    bot_chat = Bot(CHAT_BOT_TOKEN, parse_mode=ParseMode.HTML)

    dp_deal.include_routers(
        main_handlers.main_router,
        auth_router,
        joining_users_router
    )

    dp_chatbot.include_routers(
        main_router
    )

    dp_deal.startup.register(on_startup_bot)
    dp_chatbot.startup.register(on_startup_chatbot)

    app_deal = web.Application()
    app_chat = web.Application()

    SimpleRequestHandler(
        dispatcher=dp_deal, bot=bot_deal, secret_token=WEBHOOK_SECRET_BOT,
    ).register(app_deal, path=WEBHOOK_PATH_BOT)

    SimpleRequestHandler(
        dispatcher=dp_chatbot, bot=bot_chat, secret_token=WEBHOOK_SECRET_CHATBOT
    ).register(app_chat, path=WEBHOOK_PATH_CHATBOT)

    setup_application(app_deal, dp_deal, bot=bot_deal)
    setup_application(app_chat, dp_chatbot, bot=bot_chat)

    setup_dialogs(dp_deal)
    setup_dialogs(dp_chatbot)

    web.run_app(app_deal, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT_DEAL)
    web.run_app(app_chat, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT_CHAT)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()
