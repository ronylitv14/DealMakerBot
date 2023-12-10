import random
from typing import Any

from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.dialog import DialogManager
from aiogram.types import Message, CallbackQuery
from aiogram_dialog.widgets.kbd import Button

from database.crud import UserType, get_similarity_users, save_task_to_db
from database.models import User, PropositionBy, TaskStatus
from utils.dialog_categories import subject_titles
from utils.channel_creating import creating_chat_for_users, TELEGRAM_USER

class InputCallback:
    @staticmethod
    async def process_query_input_executor(message: Message, widget: MessageInput, manager: DialogManager):
        query = message.text

        executors = await get_similarity_users(name=query, is_executor=True)
        manager.dialog_data["executors"] = executors
        await manager.next()

    @staticmethod
    async def process_query_input_client(message: Message, widget: MessageInput, manager: DialogManager):
        query = message.text

        clients = await get_similarity_users(name=query, is_executor=False)
        manager.dialog_data["clients"] = clients
        await manager.next()

    @staticmethod
    async def process_description(message: Message, widget: MessageInput, manager: DialogManager):
        desc = message.text
        manager.dialog_data["description"] = desc
        await manager.next()


class SelectCallbacks:
    @staticmethod
    async def on_executor_selected(callback: CallbackQuery, widget: Any,
                                   manager: DialogManager, item_id: str):
        if item_id == "-1":
            return await callback.answer("Немає знайдених користувачів")

        executors = manager.dialog_data.get("executors")
        executor = executors[int(item_id)]

        manager.dialog_data["executor"] = executor
        await manager.next()

    @staticmethod
    async def on_client_selected(callback: CallbackQuery, widget: Any,
                                 manager: DialogManager, item_id: str):
        if item_id == "-1":
            return await callback.answer("Немає знайдених користувачів")

        clients = manager.dialog_data.get("clients")
        client = clients[int(item_id)]

        manager.dialog_data["client"] = client
        await manager.next()

    @staticmethod
    async def on_subject_selected(callback: CallbackQuery, widget: Any,
                                  manager: DialogManager, item_id: str):
        if item_id == "-1":
            return await callback.answer("Немає знайдених користувачів")

        subject = subject_titles[int(item_id)]
        manager.dialog_data["subject"] = subject

        await manager.next()


class ButtonCallbacks:
    @staticmethod
    async def create_deal_for_all(callback: CallbackQuery, button: Button, manager: DialogManager):
        executor: User = manager.dialog_data.get("executor")
        client: User = manager.dialog_data.get("client")
        desc = manager.dialog_data.get("description")
        subject = manager.dialog_data.get("subject")

        task = await save_task_to_db(
            client_id=client.telegram_id,
            executor_id=executor.telegram_id,
            subjects=[subject],
            proposed_by=PropositionBy.executor,
            description=desc,
            status=TaskStatus.executing,
            price="Договірна",
            work_type=["Інше"]
        )

        chat_admin = random.choice(TELEGRAM_USER)

        msg_for_users = (f"Тепер ви можете перейти за посиланням до нового чату, який був створений адміністратором\n"
                        f"Стоверний він щодо предмету: <b>{subject}</b>\n\n"
                        f"Опис від адміністратора: <b>{desc}</b>")

        print(chat_admin)

        await creating_chat_for_users(
            task_id=task.task_id,
            callback=callback,
            chat_admin=chat_admin,
            executor_id=executor.telegram_id,
            client_id=client.telegram_id,
            bot=callback.bot,
            desc_client=msg_for_users,
            desc_executor=msg_for_users
        )
