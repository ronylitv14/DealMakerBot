from aiogram.types import CallbackQuery
from aiogram_dialog.dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button

from handlers.utils.email_utils import send_email_token
from database.crud import get_user_auth
from database.models import User


class ButtonCallbacks:
    @staticmethod
    async def get_token_by_mobile(callback: CallbackQuery, button: Button, manager: DialogManager):
        await callback.answer(
            text="В розробці"
        )

    @staticmethod
    async def get_token_by_email(callback: CallbackQuery, button: Button, manager: DialogManager):
        user: User = await get_user_auth(callback.from_user.id)

        send_email_token(
            receiver_address=user.email
        )

        await callback.answer(
            text="Скоро на вашу пошту прийде тимчасовий пароль"
        )

    @staticmethod
    async def cancel_dialog(callback: CallbackQuery, button: Button, manager: DialogManager):
        pass
