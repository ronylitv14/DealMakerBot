from aiogram.types import CallbackQuery
from aiogram_dialog.widgets.kbd import Button, ScrollingGroup
from aiogram_dialog.dialog import DialogManager
from aiogram_dialog.widgets.text import Const

from database.crud import get_orders, get_executor_orders
from database.models import TaskStatus, Executor
from keyboards.clients import create_keyboard_client
from keyboards.executors import create_keyboard_executor
from handlers.states_handler import ClientDialog, ExecutorDialog
from database.crud import UserType

from .window_state import MyOrders


class ButtonCallbacks:

    @staticmethod
    async def get_active_orders(callback: CallbackQuery, button: Button, manager: DialogManager):
        user_type: UserType = manager.dialog_data.get("user_type")
        executor: Executor = manager.dialog_data.get("executor")

        if user_type == UserType.executor:
            active_orders = await get_executor_orders(
                executor.executor_id,
                TaskStatus.active,
                TaskStatus.executing
            )
        else:
            active_orders = await get_orders(
                callback.from_user.id,
                user_type,
                TaskStatus.executing
            )

        if active_orders:
            manager.dialog_data["orders"] = active_orders
            await manager.switch_to(MyOrders.watch_orders)
        else:
            await callback.message.answer(
                text="У вас немає активних замовлень"
            )

    @staticmethod
    async def get_finished_orders(callback: CallbackQuery, button: Button, manager: DialogManager):
        user_type: UserType = manager.dialog_data.get("user_type")
        executor: Executor = manager.dialog_data.get("executor")

        if executor:
            finished_orders = await get_executor_orders(
                executor.executor_id,
                TaskStatus.done
            )
        else:
            finished_orders = await get_orders(
                callback.from_user.id,
                user_type,
                TaskStatus.done
            )

        if finished_orders:
            manager.dialog_data["orders"] = finished_orders
            await manager.switch_to(MyOrders.watch_orders)
        else:
            await callback.message.answer(
                text="На даний момент у вас немає виконаних замовлень"
            )

    @staticmethod
    async def cancel_dialog(callback: CallbackQuery, button: Button, manager: DialogManager):
        cur_state = manager.dialog_data.get("cur_state")

        await manager.done()
        await callback.message.answer(
            text="Виходимо з режиму огляду замовлень",
            reply_markup=create_keyboard_client() if cur_state == ClientDialog.client_state else create_keyboard_executor()
        )
