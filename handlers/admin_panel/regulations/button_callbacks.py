from aiogram.types import CallbackQuery
from aiogram_dialog.dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button

from database_api.components.users import Users, UserResponse


async def ban_user(callback: CallbackQuery, button: Button, manager: DialogManager):

    user = manager.start_data.get("user")

    await Users().ban_user(
        user_id=user["telegram_id"],
        is_banned=True
    ).do_request()

    await manager.done()


async def unban_user(callback: CallbackQuery, button: Button, manager: DialogManager):

    user: UserResponse = manager.start_data.get("user")

    await Users().ban_user(
        user_id=user["telegram_id"],
        is_banned=False
    ).do_request()
    await manager.done()


async def add_warning(callback: CallbackQuery, button: Button, manager: DialogManager):
    await manager.next()
