from aiogram import F
from aiogram.enums import ChatType
from aiogram.dispatcher.router import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from aiogram_dialog.dialog import DialogManager
from aiogram_dialog.api.entities import StartMode

from handlers.tickets.window_state import Tickets
from handlers.tickets.dialog_windows import create_tickets_dialog

ticket_router = Router()
ticket_router.message.filter(F.chat.type.in_({ChatType.PRIVATE, ChatType.GROUP, ChatType.SUPERGROUP}))
ticket_router.include_routers(create_tickets_dialog())


@ticket_router.message(
    Command("ticket")
)
async def create_ticket(message: Message, dialog_manager: DialogManager):
    await message.answer(
        text="Перейдемо до створення тікету!",
        reply_markup=ReplyKeyboardRemove()
    )

    await dialog_manager.start(
        state=Tickets.add_subject,
        mode=StartMode.RESET_STACK
    )
