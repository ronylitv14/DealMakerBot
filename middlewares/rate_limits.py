from typing import Callable, Dict, Any, Awaitable
from functools import lru_cache

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag, extract_flags
from aiogram.dispatcher.event.handler import HandlerObject
from aiogram.types import Message, CallbackQuery, KeyboardButton, ReplyKeyboardMarkup, TelegramObject
from datetime import datetime, timedelta


class RateLimitMiddleware(BaseMiddleware):

    def __init__(self):
        self.user_data = {}

    async def __call__(self,
                       handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
                       event: CallbackQuery,
                       data: Dict[str, Any]) -> Any:
        if event.data not in ["random_data", "create-chat"]:
            return await handler(event, data)

        if cur_date := self.user_data.get(event.from_user.id):
            if (datetime.utcnow() - cur_date) < timedelta(seconds=30):
                await event.answer("Зачекайте поки спрацює минулий виклик!")
                return await event.answer()

        self.user_data[event.from_user.id] = datetime.utcnow()
        await handler(event, data)
