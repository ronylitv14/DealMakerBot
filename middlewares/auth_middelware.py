from typing import Callable, Dict, Any, Awaitable, Optional

from aiogram import BaseMiddleware

from aiogram.types import CallbackQuery, KeyboardButton, ReplyKeyboardMarkup

from database_api.components.users import Users, UserResponse
from database_api.components.executors import Executors, ExecutorModel, ProfileStatus


class InnerAuthMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        # res = await get_user_auth(event.from_user.id)
        res: Optional[UserResponse] = await Users().get_user_from_db(event.from_user.id).do_request()
        if not isinstance(res, UserResponse):
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

        executor_profile: ExecutorModel = await Executors().get_executor_data(event.from_user.id).do_request()

        if not executor_profile:
            await event.answer(text="Вашаго профілю поки немає в боті! Потрібно зареєструватись")
            return await handler(event, data)

        if executor_profile.profile_state == ProfileStatus.created:
            return await event.answer(text="Ваш профіль поки розглядають, тому потрібно зачекати!")
        return await handler(event, data)
