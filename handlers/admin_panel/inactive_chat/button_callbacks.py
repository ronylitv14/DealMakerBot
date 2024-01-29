from typing import Type

from aiogram.types import Message, CallbackQuery
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.dialog import DialogManager

from abc import ABC, abstractmethod

from aiogram_dialog.widgets.kbd import Button

from database_api.components.chats import Chats, ChatModel
from database_api.components.tasks import Tasks, TaskModel

from handlers.utils.unused_chats_utils import create_inactive_chat


class InputChatInfoHandler(ABC):
    def __init__(self, message_text: str):
        self.message_text = message_text

    @abstractmethod
    def process_input(self):
        pass


class HandleIntInput(InputChatInfoHandler):

    def process_input(self):
        return int(self.message_text)


class HandlerGroupInput(InputChatInfoHandler):

    def process_input(self):
        return int(self.message_text.split("№")[-1])


class UnknownInput(BaseException):
    pass


class InputChatFactory:
    def __init__(self, message: Message):
        self.message = message

    def get_handler(self) -> InputChatInfoHandler:
        if self.message.text.isdigit():
            return HandleIntInput(message_text=self.message.text)
        elif self.message.text.isalpha():
            return HandlerGroupInput(message_text=self.message.text)
        raise UnknownInput("No matched handler for text!")


class ButtonCallbacks:
    @staticmethod
    async def process_chat_id(message: Message, widget: MessageInput, manager: DialogManager):
        db_chat_id: int = InputChatFactory(message=message).get_handler().process_input()

        try:
            chat: ChatModel = await Chats().get_chat_data(db_chat_id=db_chat_id).do_request()
            task: TaskModel = await Tasks().get_task_data(task_id=chat.task_id).do_request()
        except AttributeError as err:
            await message.answer("Такого номеру чату, на жаль, немає. Можливо виникла помилка в БД!")
            return

        manager.dialog_data["chat"] = chat
        manager.dialog_data["task"] = task.create_task_summary()

        await manager.next()

    @staticmethod
    async def accept_chat_deactivation(callback: CallbackQuery, button: Button, manager: DialogManager):
        chat: ChatModel = manager.dialog_data.get("chat")

        res = await create_inactive_chat(
            db_chat_id=chat.id,
            bot=callback.bot,
            admin_id=callback.from_user.id
        )
        if not res:
            await callback.message.answer("Не вдалось виконати очікувану дію!")
        else:
            await callback.message.answer("Тепер цей чат вільний!")
        await manager.done()

    @staticmethod
    async def reject_chat_deactivation(callback: CallbackQuery, button: Button, manager: DialogManager):
        await callback.message.answer("Спробуйте ще раз, або покиньте діалог за допомогою кнопки 'Вийти'")
        await manager.done()
