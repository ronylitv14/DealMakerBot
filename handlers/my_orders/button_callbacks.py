from aiogram.types import CallbackQuery
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.dialog import DialogManager

from keyboards.clients import create_keyboard_client
from keyboards.executors import create_keyboard_executor
from handlers.states_handler import ClientDialog

from database_api.components.users import UserType
from database_api.components.executors import Executors, ExecutorModel
from database_api.components.tasks import Tasks, TaskStatus, TasksList

from handlers.my_orders.window_state import MyOrders


class ButtonCallbacks:

    @staticmethod
    async def get_active_orders(callback: CallbackQuery, button: Button, manager: DialogManager):
        user_type: UserType = manager.dialog_data.get("user_type")
        executor = manager.dialog_data.get("executor")

        if user_type == UserType.executor:

            active_orders: TasksList = await Executors().get_executor_tasks(
                status=[TaskStatus.active, TaskStatus.executing],
                executor_id=executor["user_id"]
            ).do_request()

        else:
            active_orders: TasksList = await Tasks().get_all_user_tasks(
                user_id=callback.from_user.id,
                user_type=user_type,
                task_status=[TaskStatus.active, TaskStatus.executing]
            ).do_request()

        if active_orders:
            manager.dialog_data["orders"] = active_orders.model_dump(mode="json")
            await manager.switch_to(MyOrders.watch_orders)
        else:
            await callback.message.answer(
                text="У вас немає активних замовлень"
            )

    @staticmethod
    async def get_finished_orders(callback: CallbackQuery, button: Button, manager: DialogManager):
        user_type: UserType = manager.dialog_data.get("user_type")
        executor = manager.dialog_data.get("executor")

        if executor:
            finished_orders = await Executors().get_executor_tasks(
                status=[TaskStatus.done],
                executor_id=executor["user_id"]
            ).do_request()
        else:
            finished_orders = await Tasks().get_all_user_tasks(
                user_id=callback.from_user.id,
                user_type=user_type,
                task_status=[TaskStatus.done]
            ).do_request()

        if finished_orders:
            manager.dialog_data["orders"] = finished_orders.model_dump(mode="json")
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
