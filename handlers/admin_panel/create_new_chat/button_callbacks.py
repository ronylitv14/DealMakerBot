import random
from typing import Any

from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.dialog import DialogManager
from aiogram.types import Message, CallbackQuery
from aiogram_dialog.widgets.kbd import Button

from database_api.components.users import Users, UserResponse, UserResponseList
from database_api.components.tasks import Tasks, TaskModel, PropositionBy, TaskStatus

from utils.dialog_categories import subject_titles
from utils.channel_creating import creating_chat_for_users, TELEGRAM_USER
from handlers.utils.unused_chats_utils import check_existence_and_create_new_deal


class InputCallback:
    @staticmethod
    async def process_query_input_executor(message: Message, widget: MessageInput, manager: DialogManager):
        query = message.text

        executors: UserResponseList = await Users().get_similar_users(
            name=query,
            is_executor=True
        ).do_request()

        if not isinstance(executors, UserResponseList):
            return await message.answer("Спробуйте ще раз! Таких користувачів не знайдено!")

        manager.dialog_data["executors"] = executors.model_dump(mode="json")
        await manager.next()

    @staticmethod
    async def process_query_input_client(message: Message, widget: MessageInput, manager: DialogManager):
        query = message.text

        clients: UserResponseList = await Users().get_similar_users(
            name=query,
            is_executor=False
        ).do_request()
        print(clients)

        if not isinstance(clients, UserResponseList):
            return await message.answer("Спробуйте ще раз! Таких користувачів не знайдено!")

        manager.dialog_data["clients"] = clients.model_dump(mode="json")
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
        executor = executors["list_values"][int(item_id)]

        user_summary = f"Ім'я користувача: {executor['username']}, статус: {executor['user_status']}"

        manager.dialog_data["executor"] = executor
        manager.dialog_data["executor_summary"] = user_summary
        await manager.next()

    @staticmethod
    async def on_client_selected(callback: CallbackQuery, widget: Any,
                                 manager: DialogManager, item_id: str):
        if item_id == "-1":
            return await callback.answer("Немає знайдених користувачів")

        clients = manager.dialog_data.get("clients")
        client = clients["list_values"][int(item_id)]

        user_summary = f"Ім'я користувача: {client['username']}, статус: {client['user_status']}"

        manager.dialog_data["client"] = client
        manager.dialog_data["client_summary"] = user_summary
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
        executor = UserResponse(**manager.dialog_data.get("executor"))
        client = UserResponse(**manager.dialog_data.get("client"))

        desc = manager.dialog_data.get("description")
        subject = manager.dialog_data.get("subject")

        task: TaskModel = await Tasks().save_task_data(
            client_id=client.telegram_id,
            executor_id=executor.telegram_id,
            subjects=[subject],
            proposed_by=PropositionBy.executor,
            description=desc,
            status=TaskStatus.executing,
            price="Договірна",
            work_type=["Інше"]
        ).do_request()

        if not isinstance(task, TaskModel):
            await callback.message.answer("Сталася помилка при збережені замовлення!\nСпробуйте пізніше!")
            await manager.done()
            return

        chat_admin = random.choice(TELEGRAM_USER)

        msg_for_users = (f"Тепер ви можете перейти за посиланням до нового чату, який був створений адміністратором\n"
                         f"Стоверний він щодо предмету: <b>{subject}</b>\n\n"
                         f"Опис від адміністратора: <b>{desc}</b>")

        print(chat_admin)

        try:
            await check_existence_and_create_new_deal(
                bot=callback.bot,
                callback=callback,
                task_id=task.task_id,
                client_id=client.telegram_id,
                executor_id=executor.telegram_id
            )
            await manager.done()
            return
        except ValueError as err:
            print(f"No free chats availiable - {err}")

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

        await manager.done()
        await callback.answer("Чат створено!")
