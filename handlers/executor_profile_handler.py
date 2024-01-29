from aiogram import F
from aiogram import types
from aiogram.enums import ChatType
from aiogram.fsm.context import FSMContext
from aiogram.dispatcher.router import Router
from aiogram_dialog.dialog import DialogManager
from aiogram_dialog.api.entities import StartMode

from handlers.states_handler import ExecutorDialog
from handlers.creating_executor_profile.window_state import CreatingProfile
from handlers.creating_executor_profile.dialog_windows import add_dialog_to_router
from handlers.my_orders.window_state import MyOrders
from keyboards.executors import create_keyboard_executor


from database_api.components.executors import ProfileStatus, Executors, ExecutorModel

executor_router = Router()

executor_router.message.filter(F.chat.type.in_({ChatType.PRIVATE}))
add_dialog_to_router(executor_router)


@executor_router.message(
    F.text.contains("📖"),
)
async def get_executor_menu(message: types.Message, state: FSMContext, dialog_manager: DialogManager):

    executor: ExecutorModel = await Executors().get_executor_data(message.from_user.id).do_request()

    await state.set_data({"executor": executor})
    if not isinstance(executor, ExecutorModel):
        await message.answer(
            text="Перевірка на присутність у базі даних виконавців",
            reply_markup=types.ReplyKeyboardRemove()
        )

        await dialog_manager.start(state=CreatingProfile.adding_description, mode=StartMode.RESET_STACK)
        dialog_manager.dialog_data["cur_state"] = await state.get_state()
        dialog_manager.dialog_data["state_obj"] = state
        dialog_manager.dialog_data["docs"] = []
        dialog_manager.dialog_data["type"] = []
        return

    if executor.profile_state == ProfileStatus.created:
        return await message.answer(text="Ваша заявка поки розглядається!")
    elif executor.profile_state == ProfileStatus.rejected:
        await message.answer(text="Ваша заявка відхилена!")
        await dialog_manager.start(state=CreatingProfile.adding_description, mode=StartMode.RESET_STACK)
        dialog_manager.dialog_data["cur_state"] = await state.get_state()
        dialog_manager.dialog_data["state_obj"] = state
        dialog_manager.dialog_data["docs"] = []
        dialog_manager.dialog_data["type"] = []
        return

    await state.set_state(ExecutorDialog.executor_state)
    await message.answer(
        text="Тепер ти на профілі виконавця",
        reply_markup=create_keyboard_executor()
    )


@executor_router.message(
    F.text.contains("📄"),
    ExecutorDialog.executor_state
)
async def get_executor_orders(message: types.Message, state: FSMContext, dialog_manager: DialogManager):
    await message.answer(
        text="Checking executor orders"
    )
    data = await state.get_data()
    executor = data.get("executor")

    await dialog_manager.start(state=MyOrders.main, mode=StartMode.RESET_STACK)
    dialog_manager.dialog_data["executor"] = executor
