from aiogram.types import CallbackQuery
from aiogram_dialog.dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button

from database.crud import update_ban_status
from database.models import User, Warning


async def ban_user(callback: CallbackQuery, button: Button, manager: DialogManager):
    user: User = manager.start_data.get("user")

    await update_ban_status(
        user_id=user.telegram_id,
        is_banned=True
    )

    await manager.done()


async def unban_user(callback: CallbackQuery, button: Button, manager: DialogManager):
    user: User = manager.start_data.get("user")

    await update_ban_status(
        user_id=user.telegram_id,
        is_banned=False
    )
    await manager.done()


async def add_warning(callback: CallbackQuery, button: Button, manager: DialogManager):
    await manager.next()
