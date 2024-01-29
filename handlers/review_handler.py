from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from aiogram_dialog.dialog import DialogManager
from aiogram_dialog.api.entities import StartMode

from keyboards.inline_keyboards import CallbackConstructorReview

from handlers.create_review.dialog_states import ReviewStates
from handlers.create_review.dialog_windows import create_review_dialog

review_router = Router()
review_router.include_router(create_review_dialog())


@review_router.callback_query(
    F.data.startswith("accept-review")
)
async def start_review_dialog(callback: CallbackQuery, state: FSMContext, dialog_manager: DialogManager):
    reviewer_id, reviewed_id, task_id = CallbackConstructorReview.split_callback_data(callback.data)

    cur_state = await state.get_state()

    await dialog_manager.start(
        state=ReviewStates.specify_rating,
        mode=StartMode.RESET_STACK,
        data=dict(
            reviewer_id=reviewer_id,
            reviewed_id=reviewed_id,
            task_id=task_id,
            cur_state=cur_state,
            state_obj=state
        )
    )


@review_router.callback_query(
    F.data.startswith("reject-review")
)
async def reject_review_dialog(callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer("Добре, сподіваюсь Ви були задоволені роботою у нашому додатку!")
