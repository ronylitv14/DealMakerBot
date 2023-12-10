import asyncio
import os
from datetime import date
from dotenv import load_dotenv

from aiogram.types.message import ContentType
from aiogram.types import Message, CallbackQuery, FSInputFile

from aiogram_dialog.widgets.input import MessageInput

from aiogram_dialog import (
    DialogManager
)
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.api.entities import ShowMode
from aiogram.fsm.context import FSMContext

from utils.dialog_categories import subject_titles, university_tasks
from keyboards.clients import create_keyboard_client
from .window_state import OrderState
from keyboards.inline_keyboards import create_group_message_keyboard
from utils.group_msg_template import create_group_message

from aiogram_dialog.widgets.kbd import Multiselect

from database.crud import save_task_to_db, update_task_files, add_group_message
from database.models import TaskStatus, Task, FileType

load_dotenv()

group_name = os.getenv('TG_GROUP_NAME')


class AddingGroupMessage:
    def __init__(self, callback: CallbackQuery, manager: DialogManager, task: Task):
        self.callback = callback
        self.manager = manager
        self.task = task

    async def add_group_message(self, group_name):
        group_message = create_group_message(
            task_status=self.task.status.value,
            task_types=self.task.work_type,
            task_subjects=self.task.subjects,
            task_deadline=self.task.deadline,
            task_description=self.task.description,
            task_price=self.task.price,
        )

        bot = self.callback.bot

        files, files_type = self.task.files, self.task.files_type

        msg = await bot.send_message(
            chat_id=group_name,
            text=group_message,
            reply_markup=create_group_message_keyboard(
                task_id=self.task.task_id,
                has_files=True if files else False
            )
        )

        is_saved = await add_group_message(
            group_message_id=msg.message_id,
            task_id=self.task.task_id,
            message_text=group_message,
            has_files=True if files else False
        )

        if not is_saved:
            await msg.delete()


class ButtonCallbacks:
    @staticmethod
    async def saving_task_type_data(callback: CallbackQuery, button: Button, manager: DialogManager):
        result_widget: Multiselect = manager.find("m_task_type")
        data = result_widget.get_checked()
        data = [university_tasks[int(t)] for t in data]
        manager.dialog_data["task_type"] = data
        await manager.next()

    @staticmethod
    async def saving_subject_title_data(callback: CallbackQuery, button: Button, manager: DialogManager):
        result_widget: Multiselect = manager.find("m_subjects")
        data = result_widget.get_checked()

        data = [subject_titles[int(sub_ind)] for sub_ind in data]
        manager.dialog_data["subject_title"].extend(data)
        await manager.next()

    @staticmethod
    async def set_subject(message: Message, input_widget: MessageInput, manager: DialogManager):
        manager.dialog_data["subject_title"].extend([message.text])
        await manager.next()

    @staticmethod
    async def create_price(message: Message, input_widget: MessageInput, manager: DialogManager):
        price_value = message.text
        if price_value.isdigit():
            manager.dialog_data["price"] = price_value
            # await manager.switch_to(OrderState.deadline)
            await manager.next()
        else:
            await message.answer(
                text="Не коректно введене значення ціни! Потрібно просто ввести цифри у вигляді: 200, 300 тощо"
            )

    @staticmethod
    async def set_price_unknown(callback: CallbackQuery, button: Button, manager: DialogManager):
        manager.dialog_data["price"] = "Договірна"
        await manager.next()

    @staticmethod
    async def set_deadline(callback: CallbackQuery, widget,
                           manager: DialogManager, selected_date: date):
        manager.dialog_data["date"] = selected_date
        await manager.switch_to(OrderState.adding_description)

    @staticmethod
    async def preprocess_files_input(message: Message, input_widget: MessageInput, manager: DialogManager):
        manager.show_mode = ShowMode.EDIT
        file = None
        filename = None

        if message.content_type == ContentType.DOCUMENT:
            file, filename = message.document.file_id, message.document.file_name
            manager.dialog_data["type"].append(FileType.document)
        elif message.content_type == ContentType.PHOTO:
            file, filename = message.photo[0].file_id, "фото"
            manager.dialog_data["type"].append(FileType.photo)

        manager.dialog_data["docs"].append(file)
        manager.dialog_data["last_document"] = file

        if message.media_group_id:
            await message.answer(text=f"Додано документ з назвою {filename}")
            await asyncio.sleep(1)
            if manager.dialog_data["last_document"] == file:
                manager.show_mode = ShowMode.SEND
                await message.answer(
                    text=f"Якщо це всі документи, що вам потрібно натискайте 'Зберегти' і ваше замовлення скоро з'явиться у групі")
        else:
            await message.answer(text=f"Додано документ з назвою {filename}")
            manager.show_mode = ShowMode.SEND
            await message.answer(
                text=f"Якщо це всі документи, що вам потрібно натискайте 'Зберегти' і ваше замовлення скоро з'явиться у групі")

    @staticmethod
    async def save_order(callback: CallbackQuery, button: Button, manager: DialogManager):

        task = await save_task_to_db(
            client_id=callback.from_user.id,
            description=manager.dialog_data.get('desc'),
            price=manager.dialog_data.get('price'),
            deadline=manager.dialog_data.get('date'),
            subjects=manager.dialog_data.get('subject_title'),
            files=manager.dialog_data.get("docs", []),
            files_type=manager.dialog_data.get("type", []),
            status=TaskStatus.active,
            work_type=manager.dialog_data.get('task_type'),
        )

        # if files_list := manager.dialog_data.get('docs'):
        #     # results_paths = await download_files(
        #     #     bot=callback.bot,
        #     #     files_list=files_list,
        #     #     user_tg_id=callback.from_user.id,
        #     #     task_id=task.task_id,
        #     # )
        #
        #     task = await update_task_files(
        #         files=files_list,
        #         task_id=task.task_id
        #     )

        await manager.done()
        await callback.answer(text='Зберігаємо дані до групи! Це може зайняти якийсь час....')
        await asyncio.sleep(0.5)
        adding_msg = AddingGroupMessage(
            callback=callback,
            manager=manager,
            task=task
        )
        await adding_msg.add_group_message(group_name)
        await callback.message.answer(
            text="Збережено",
            reply_markup=create_keyboard_client()
        )

    @staticmethod
    async def preprocess_desc(message: Message, input_widget: MessageInput, manager: DialogManager):
        if message.content_type != ContentType.TEXT and not message.text.isalpha():
            await message.answer(
                text="Не коректно введений опис для завдання спробуйте ще раз!"
            )
        else:
            manager.dialog_data["desc"] = message.text
            # await manager.switch_to(OrderState.adding_materials)
            await manager.next()

    @staticmethod
    async def skip_dialog_window(callback: CallbackQuery, button: Button, manager: DialogManager):
        await manager.next()

    @staticmethod
    async def cancel_creating_order(callback: CallbackQuery, button: Button, manager: DialogManager):
        await manager.done()
        await callback.message.answer(
            text="Відмінено створення замовлення",
            reply_markup=create_keyboard_client(),
        )
