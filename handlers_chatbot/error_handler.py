from aiogram import Router
from aiogram import types
from aiogram_dialog.api.exceptions import UnknownIntent, OutdatedIntent

error_router = Router()


@error_router.error()
async def handle_outdated_intent(event: types.ErrorEvent):
    if isinstance(event.exception, UnknownIntent) or isinstance(event.exception, OutdatedIntent):
        return event.update.callback_query.answer(
            "Час дії діалогу минув! Спробуйте створити новий")
    raise event.exception
