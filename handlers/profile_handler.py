from aiogram import Router, F
from aiogram.filters import BaseFilter
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.enums import ChatType

from aiogram_dialog.dialog import DialogManager
from aiogram_dialog.api.entities import StartMode
from handlers.states_handler import ExecutorDialog, ClientDialog, ProfileDialog
from keyboards.clients import create_profile_instruments, create_keyboard_client
from keyboards.executors import create_keyboard_executor

from handlers.profile_instruments.window_state import *
from handlers.reset_password.window_state import *
from handlers.profile_instruments.dialog_windows import create_dialogs

from middlewares.auth_middelware import InnerAuthMiddleware

profile_router = Router()
profile_router.message.filter(F.chat.type.in_({ChatType.PRIVATE}))

profile_router.include_routers(*create_dialogs())
profile_router.message.middleware(InnerAuthMiddleware())


class StateFilter(BaseFilter):
    def __init__(self, *states, **kwargs):
        super().__init__(**kwargs)
        self.states = states

    async def __call__(self, *args, **kwargs):
        state = kwargs.get("state")
        cur_state = await state.get_state()
        if cur_state in self.states:
            return True
        return False


@profile_router.message(
    F.text.contains("💂"),
    StateFilter(ExecutorDialog.executor_state, ClientDialog.client_state)
)
async def start_profile_dialog(message: Message, state: FSMContext):
    cur_state = await state.get_state()
    if cur_state == ClientDialog.client_state:
        await state.set_state(ClientDialog.profile)
        await message.answer(
            text="Оберіть потрібну вам команду",
            reply_markup=create_profile_instruments()
        )
    elif cur_state == ExecutorDialog.executor_state:
        await state.set_state(ExecutorDialog.profile)
        await message.answer(
            text="Оберіть потрібну вам команду",
            reply_markup=create_profile_instruments()
        )
    else:
        await message.answer(text="Щось пішло не так")


@profile_router.message(
    F.text.contains("☎"),
    StateFilter(ExecutorDialog.profile, ClientDialog.profile)
)
async def on_phone_edit(message: Message, state: FSMContext, dialog_manager: DialogManager):
    cur_state = await state.get_state()
    await state.set_state(ProfileDialog.edit_phone)
    await message.answer(
        text="Вікно для телефона",
        reply_markup=ReplyKeyboardRemove()
    )
    await dialog_manager.start(state=EditPhone.auth_user, mode=StartMode.RESET_STACK)
    dialog_manager.dialog_data["state"] = state
    dialog_manager.dialog_data["cur_state"] = cur_state


@profile_router.message(
    F.text.contains("🖊"),
    StateFilter(ExecutorDialog.profile, ClientDialog.profile)
)
async def on_password_reset(message: Message, state: FSMContext, dialog_manager: DialogManager):
    cur_state = await state.get_state()

    await state.set_state(ProfileDialog.edit_password)
    await message.answer(
        text="Вікно для пароля",
        reply_markup=ReplyKeyboardRemove()
    )
    await dialog_manager.start(state=EditPassword.choose_option, mode=StartMode.RESET_STACK)
    dialog_manager.dialog_data["cur_state"] = cur_state
    dialog_manager.dialog_data["state"] = state


@profile_router.message(
    F.text.contains("🧛"),
    StateFilter(ExecutorDialog.profile, ClientDialog.profile)
)
async def on_nickname_edit(message: Message, state: FSMContext, dialog_manager: DialogManager):
    cur_state = await state.get_state()
    await state.set_state(ProfileDialog.edit_name)
    await message.answer(
        text="Вікно для нікнейма",
        reply_markup=ReplyKeyboardRemove()
    )
    await dialog_manager.start(state=EditNickName.auth_user, mode=StartMode.RESET_STACK)
    dialog_manager.dialog_data["cur_state"] = cur_state
    dialog_manager.dialog_data["state"] = state


@profile_router.message(
    F.text.contains("📪"),
    StateFilter(ExecutorDialog.profile, ClientDialog.profile)
)
async def on_email_edit(message: Message, state: FSMContext, dialog_manager: DialogManager):
    cur_state = await state.get_state()
    await state.set_state(ProfileDialog.edit_email)
    await message.answer(
        text="Вікно для пошти",
        reply_markup=ReplyKeyboardRemove()
    )
    await dialog_manager.start(state=EditMail.auth_user, mode=StartMode.RESET_STACK)
    dialog_manager.dialog_data["cur_state"] = cur_state
    dialog_manager.dialog_data["state"] = state


@profile_router.message(
    F.text.contains("⛔"),
    StateFilter(ExecutorDialog.profile, ClientDialog.profile)
)
async def on_account_deletion(message: Message, state: FSMContext, dialog_manager: DialogManager):
    cur_state = await state.get_state()
    await state.set_state(ProfileDialog.delete_account)
    await message.answer(
        text="Вікно для Видалення",
        reply_markup=ReplyKeyboardRemove()
    )
    await dialog_manager.start(DeleteAccount.auth_user, mode=StartMode.RESET_STACK)
    dialog_manager.dialog_data["cur_state"] = cur_state
    dialog_manager.dialog_data["state"] = state
    dialog_manager.dialog_data["delete"] = True


@profile_router.message(
    F.text.contains("🔙"),
    ExecutorDialog.profile
)
async def back_to_menu_executor(message: Message, state: FSMContext):
    await message.answer(
        text="Переходимо до меню виконавця",
        reply_markup=create_keyboard_executor()
    )
    await state.set_state(ExecutorDialog.executor_state)


@profile_router.message(
    F.text.contains("🔙"),
    ClientDialog.profile
)
async def back_to_menu_executor(message: Message, state: FSMContext):
    await message.answer(
        text="Переходимо до меню клієнта",
        reply_markup=create_keyboard_client()
    )
    await state.set_state(ClientDialog.client_state)
