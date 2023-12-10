from aiogram import Bot, F
from aiogram.enums import ChatType
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.dispatcher.router import Router
from aiogram.filters.command import Command, CommandException

from aiogram_dialog.dialog import DialogManager
from aiogram_dialog.api.entities import StartMode, ShowMode

from handlers.admin_panel.regulations.bans import create_regulations_dialog
from handlers.admin_panel.dialog_windows import create_admin_panel_dialog, create_application_dialog, \
    create_users_dialog, create_balance_dialog, create_withdraw_dialog, create_ticket_dialog
from handlers.admin_panel.window_states import AdminPanel
from handlers.admin_panel.create_new_chat.dialog_windows import create_custom_chat_dialog

from database.crud import get_user_auth
from database.models import User, UserStatus

admin_panel_router = Router()

admin_panel_router.message.filter(F.chat.type.in_({ChatType.PRIVATE}))

admin_panel_router.include_routers(create_admin_panel_dialog(), create_application_dialog(),
                                   create_users_dialog(), create_balance_dialog(), create_withdraw_dialog(),
                                   create_regulations_dialog(), create_ticket_dialog(), create_custom_chat_dialog())


@admin_panel_router.message(
    Command("panel")
)
async def run_admin_panel(message: Message, bot: Bot, state: FSMContext, dialog_manager: DialogManager):
    user: User = await get_user_auth(message.from_user.id)

    if not user:
        return await message.answer(text="Треба зареєструватись в системі!")

    if user.user_status not in [UserStatus.admin, UserStatus.superuser]:
        return await message.answer(text="У вас недостатньо прав для цієї команди!")

    await message.answer(
        text="Переходимо до роботи адміна!",
        reply_markup=ReplyKeyboardRemove()
    )

    await dialog_manager.start(
        state=AdminPanel.main_panel,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.SEND
    )
