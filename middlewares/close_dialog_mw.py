import asyncio
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
from aiogram_dialog.dialog import DialogManager

from handlers.utils.command_utils import show_menu
from handlers.tickets_handler import start_ticket_dialog
from handlers.admin_handler import start_admin_dialog
# from handlers_chatbot.start_handler import start_get_chat_dialog
from handlers_chatbot.utils.start_dialog_actions import start_get_chat_dialog


class CloseDialogMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]) -> Any:
        dialog_manager: DialogManager = data.get("dialog_manager")
        if dialog_manager is None:
            return await handler(event, data)

        if dialog_manager.has_context() and event.text in ["/menu", "/ticket", "/panel"]:
            await dialog_manager.done()
            match event.text:
                case "/menu":
                    return await show_menu(message=event, state=data.get("state"))
                case "/ticket":
                    return await start_ticket_dialog(message=event, dialog_manager=dialog_manager)
                case "/panel":
                    return await start_admin_dialog(message=event, dialog_manager=dialog_manager)
        return await handler(event, data)


class EndChatDialogMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]) -> Any:

        dialog_manager: DialogManager = data.get("dialog_manager")
        if dialog_manager is None:
            return await handler(event, data)

        if dialog_manager.has_context() and event.text in ["/get_chat"]:
            match event.text:
                case "/get_chat":
                    return await start_get_chat_dialog(dialog_manager=dialog_manager, message=event)

        return await handler(event, data)
