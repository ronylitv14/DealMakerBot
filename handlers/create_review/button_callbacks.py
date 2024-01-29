from typing import Optional

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button

from database_api.components.reviews import Reviews


async def saving_review(manager: DialogManager, message: Optional[Message] = None,
                        callback: Optional[CallbackQuery] = None):
    message_copy = message
    if callback:
        message_copy = callback.message

    reviewer_id = manager.start_data.get("reviewer_id")
    reviewed_id = manager.start_data.get("reviewed_id")
    task_id = manager.start_data.get("task_id")
    rating = manager.dialog_data.get("rating")
    positives = manager.dialog_data.get("positives")
    negatives = manager.dialog_data.get("negatives")
    comment = message_copy.text if not callback else None

    resp = await Reviews().save_review_data(
        reviewer_id=reviewer_id,
        reviewed_id=reviewed_id,
        task_id=task_id,
        rating=rating,
        positive_sights=positives,
        negative_sights=negatives,
        comment=comment
    ).do_request()

    if resp.is_error:
        await message_copy.answer("Помилка при збережені відгуку!")
        await manager.done()
        return
    await message_copy.answer("Дані успішно збережені")
    await manager.done()


class ButtonCallbacks:
    @staticmethod
    async def process_comment_and_dialog_end(message: Message, widget: MessageInput, manager: DialogManager):
        await saving_review(manager=manager, message=message)

    @staticmethod
    async def end_dialog(callback: CallbackQuery, button: Button, manager: DialogManager):
        await saving_review(manager=manager, callback=callback)
