import asyncio

from aiogram.types import Message, CallbackQuery
from aiogram.enums import ContentType
from aiogram_dialog.api.entities import ShowMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Multiselect
from aiogram_dialog.dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button

from keyboards.clients import create_keyboard_client
from keyboards.executors import create_keyboard_executor
from handlers.states_handler import ExecutorDialog, ClientDialog

from utils.dialog_categories import subject_titles
from database.crud import create_executor_profile
from database.models import FileType


class ButtonCallbacks:
    @staticmethod
    async def process_description(message: Message, widget: MessageInput, manager: DialogManager):
        description = message.text
        manager.dialog_data["description"] = description
        await manager.next()

    @staticmethod
    async def save_subjects(callback: CallbackQuery, button: Button, manager: DialogManager):
        subject_widget: Multiselect = manager.find("m_subjects")
        data = subject_widget.get_checked()
        data = [subject_titles[int(ind)] for ind in data]

        manager.dialog_data["subjects"] = data
        await manager.next()

    @staticmethod
    async def save_executor_application(callback: CallbackQuery, button: Button, manager: DialogManager):
        await create_executor_profile(
            user_id=callback.from_user.id,
            work_examples=manager.dialog_data.get("docs", []),
            work_files_type=manager.dialog_data.get("type", []),
            description=manager.dialog_data.get("description"),
            tags=manager.dialog_data.get("subjects")
        )

        await callback.message.answer(
            text="<b>Вашу заявку додано! Очікуйте повідомлення про підтвердження!</b>",
            parse_mode="HTML",
            reply_markup=create_keyboard_client()
        )
        await manager.done()

    @staticmethod
    async def cancel_dialog(callback: CallbackQuery, button: Button, manager: DialogManager):
        cur_state = manager.dialog_data.get("cur_state")
        await manager.done()
        await callback.message.answer(
            text="Ви вийшли з цього діалогу!",
            reply_markup=create_keyboard_client() if cur_state == ClientDialog.client_state else create_keyboard_executor()
        )
