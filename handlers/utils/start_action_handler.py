import os
from typing import List, Optional

from aiogram import types
from aiogram.methods.edit_message_text import EditMessageText
from aiogram.fsm.context import FSMContext
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram_dialog.dialog import DialogManager
from aiogram_dialog.api.entities import StartMode, ShowMode

from database_api.components.tasks import Tasks, TasksList, TaskModel, TaskStatus, FileType
from database_api.components.group_messages import GroupMessages, GroupMessageResponse
from database_api.components.users import Users, UserResponse
from database_api.components.executors import Executors, ExecutorModel

from keyboards.inline_keyboards import create_group_message_keyboard
from handlers.send_client_msg.dialog_windows import SendMessageClient

from handlers.states_handler import ClientDialog
from dotenv import load_dotenv

load_dotenv()

TG_GROUP_NAME = os.getenv("TG_GROUP_NAME")

ACTIONS = {"take_order", "check_files"}


async def change_message_status(task_id: int, message: types.Message, new_status: TaskStatus):
    group_msg: GroupMessageResponse = await GroupMessages().get_group_message_by_task(task_id).do_request()
    edited_msg = "#" + group_msg.message_text.split(sep="#", maxsplit=1)[1]
    edited_msg = f"🟠 {str(new_status)}\n\n" + edited_msg

    bot = message.bot
    await bot(
        EditMessageText(
            text=edited_msg,
            chat_id=TG_GROUP_NAME,
            message_id=group_msg.group_message_id,
            reply_markup=create_group_message_keyboard(
                task_id=task_id,
                is_active=False
            )
        )
    )


class HandleAction:
    def __init__(self, action, task_id, message: types.Message, manager: DialogManager, state: FSMContext):
        self.action = action
        self.task_id = task_id
        self.message = message
        self.manager = manager
        self.state = state

    async def choose_action(self):
        if self.action == "take_order":
            return ProcessOrder(
                message=self.message,
                task_id=self.task_id,
                dialog_manager=self.manager
            )
        elif self.action == "check_files":
            return ProcessFiles(
                message=self.message,
                task_id=self.task_id,
                state=self.state
            )
        else:
            return None


class ProcessOrder:
    def __init__(self, task_id: int, dialog_manager: DialogManager,
                 callback: Optional[types.CallbackQuery] = None, message: Optional[types.Message] = None):
        self.message = message
        self.task_id = task_id
        self.manager = dialog_manager
        self.callback = callback

    async def process_action(self):
        # TODO: Зробити так, щоб при повторному натиску кнопки викидало помилку про
        # вже взяте замовлення, або про те, що воно вже твоє
        if not any((self.callback, self.message)):
            raise ValueError

        user_id = None

        if self.message:
            user_id = self.message.from_user.id

        if self.callback:
            user_id = self.callback.from_user.id
        print(user_id)
        executor = await Executors().get_executor_data(user_id=user_id).do_request()
        if not isinstance(executor, ExecutorModel):
            return await self.message.answer(
                "Так як ви не є зареєстрованим виконавцем - це замовлення взяти неможливо!")

        task: TaskModel = await Tasks().get_task_data(task_id=self.task_id).do_request()

        if task.executor_id is not None:
            await self.message.answer(
                text="Дане замовлення вже взяте!"
            )
            return

        if task.client_id == self.message.from_user.id:
            await self.message.answer(
                text="<b>Ви не можете взяти власне замовлення</b>",
                parse_mode="HTML"
            )
            return

        executor_username: UserResponse = await Users().get_user_from_db(user_id).do_request()

        await self.manager.start(
            state=SendMessageClient.main,
            mode=StartMode.RESET_STACK,
            show_mode=ShowMode.SEND,
            data={
                "client_chat_id": task.client_id,
                "executor_tg_id": user_id,
                "task_id": task.task_id,
                "username": executor_username.telegram_username
            }
        )


async def create_files_reply(files: List[str], files_type: List[FileType], message: types.Message):
    photos = []
    docs = []

    has_files = False

    for file_id, file_type in zip(files, files_type):
        if file_type == FileType.photo:
            photos.append(types.InputMediaPhoto(media=file_id))
        elif file_type == FileType.document:
            docs.append(types.InputMediaDocument(media=file_id))

    if photos:
        media_group_photos = MediaGroupBuilder(media=photos, caption="Фото для завдання")
        await message.answer_media_group(media=media_group_photos.build())
        has_files = True

    if docs:
        media_group_docs = MediaGroupBuilder(media=docs)
        await message.answer_media_group(media=media_group_docs.build())
        has_files = True

    return has_files


class ProcessFiles:
    def __init__(self, message: types.Message, task_id: int, state: FSMContext):
        self.message = message
        self.task_id = task_id
        self.state = state

    async def process_action(self):
        await self.state.set_state(ClientDialog.client_state)
        # task: Task = await get_task(self.task_id)
        task: TaskModel = await Tasks().get_task_data(task_id=self.task_id).do_request()
        photos = []
        docs = []

        await self.message.answer(text="<b>Ось файли до завдання</b>", parse_mode="html")

        for file_id, file_type in zip(task.files, task.files_type):
            if file_type == FileType.photo:
                photos.append(types.InputMediaPhoto(media=file_id))
            elif file_type == FileType.document:
                docs.append(types.InputMediaDocument(media=file_id))

        if photos:
            media_group_photos = MediaGroupBuilder(media=photos, caption="Фото для завдання")
            await self.message.answer_media_group(media=media_group_photos.build())

        if docs:
            media_group_docs = MediaGroupBuilder(media=docs)
            await self.message.answer_media_group(media=media_group_docs.build())

        if task.client_id == self.message.from_user.id:
            await self.message.answer(
                text="Ви переглядаєте власне замовлення!"
            )
            return
        elif task.executor_id is not None:
            await self.message.answer(
                text="На жаль, це завдання вже робиться іншим виконавцем!",
                reply_markup=types.ReplyKeyboardRemove()
            )
            return

        reply_markup = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="Взяти замовлення",
                        callback_data=f"take_order-{task.task_id}"
                    )
                ]
            ]
        )

        await self.message.answer(
            text="Якщо ви ознайомились з цими файлами і готові взяти замовлення"
                 "то натисніть на кнопку нижче",
            reply_markup=reply_markup
        )
