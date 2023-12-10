from datetime import datetime
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag

from aiogram.types import Message, CallbackQuery, KeyboardButton, ReplyKeyboardMarkup, TelegramObject

from database.crud import get_user_auth, get_executor_auth
from database.models import Executor, ProfileStatus


class InnerAuthMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        res = await get_user_auth(event.from_user.id)

        if not res:
            kbd = [
                [
                    KeyboardButton(text="Відправити номер", request_contact=True),
                    KeyboardButton(text="Відмінити")
                ]
            ]

            await event.answer(
                "Ви не зареєстровані у боті!",
                reply_markup=ReplyKeyboardMarkup(keyboard=kbd, resize_keyboard=True)
            )
            return

        if res.is_banned:
            return await event.answer(
                text="<b>Вас забанила адміністрація цього сервісу!</b>\n\n"
                     "Для детальнішої інформації радимо звернутися до одного з "
                     "адміністраторів каналу для вирішення цієї проблеми!",
                parse_mode="HTML"
            )

        return await handler(event, data)


class CheckExecutorExistence(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:

        executor_profile: Executor = await get_executor_auth(event.from_user.id)

        if not executor_profile:
            await event.answer(text="Вашаго профілю поки немає в боті! Потрібно зареєструватись")
            return await handler(event, data)

        if executor_profile.profile_state == ProfileStatus.created:
            return await event.answer(text="Ваш профіль поки розглядають, тому потрібно зачекати!")
        return await handler(event, data)
