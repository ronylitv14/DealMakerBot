from aiogram import F
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.enums import ContentType, ChatType
from aiogram.dispatcher.router import Router

from aiogram_dialog.dialog import DialogManager, Dialog
from aiogram_dialog.api.entities import StartMode

from .states_handler import ClientDialog
from .auth_users.window_state import AuthStates
from .auth_users.dialog_windows import (
    username_window,
    email_window,
    first_password_window,
    second_password_window
)

auth_router = Router()
auth_router.message.filter(F.chat.type.in_({ChatType.PRIVATE}))

auth_dialog = Dialog(
    username_window,
    email_window,
    first_password_window,
    second_password_window
)

auth_router.include_routers(auth_dialog)


@auth_router.message(
    F.contact
)
async def auth_user(message: types.Message, state: FSMContext, dialog_manager: DialogManager):
    await state.set_state(ClientDialog.client_state)
    await message.answer(
        text="Отримали твій номер телефону!",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await dialog_manager.start(AuthStates.get_username, mode=StartMode.RESET_STACK)
    dialog_manager.dialog_data["phone"] = message.contact.phone_number
    dialog_manager.dialog_data["tg_username"] = message.from_user.username


@auth_router.message(
    F.text.contains("🚫")
)
async def cancel_user_auth(message: types.Message, state: FSMContext):
    await message.answer(
        text="<i>Гаразд! Відміняємо реєстрацію</i>",
        parse_mode="HTML",
        reply_markup=types.ReplyKeyboardRemove()
    )
