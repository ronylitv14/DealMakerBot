from aiogram.types import CallbackQuery
from aiogram_dialog.dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.api.entities import StartMode

from handlers.deals.window_state import CreateDeal, DealsGroup
from handlers.states_handler import ClientDialog
from keyboards.clients import create_keyboard_client
from keyboards.executors import create_keyboard_executor

from handlers.deals_executor.dialog_states import DealsExecutor

from database_api.components.tasks import TaskStatus, PropositionBy, Tasks, TasksList, TaskModel
from database_api.components.executors import Executors, ExecutorModel


def cancel_dialog_wrapper(func):
    async def decorator(callback: CallbackQuery, button: Button, manager: DialogManager):
        cur_state = await func(callback, button, manager)
        await manager.done()
        await callback.message.answer(
            text="Завершуємо цей діалог!",
            reply_markup=create_keyboard_client() if cur_state == ClientDialog.client_state else
            create_keyboard_executor()
        )

    return decorator


class ButtonCallbacks:
    @staticmethod
    async def create_deal(callback: CallbackQuery, button: Button, manager: DialogManager):

        cur_state = manager.dialog_data.get("cur_state")
        state_obj = manager.dialog_data.get("state_obj")
        proposed_by = manager.dialog_data.get("proposed_by")

        if proposed_by == PropositionBy.client:
            await manager.start(
                state=CreateDeal.choose_nickname,
                data={
                    "user_id": callback.from_user.id,
                    "cur_state": cur_state,
                    "state_obj": state_obj,
                    "proposed_by": proposed_by
                },
                mode=StartMode.RESET_STACK
            )
        elif proposed_by == PropositionBy.executor:
            await manager.start(
                state=DealsExecutor.query_user,
                mode=StartMode.RESET_STACK
            )

    @staticmethod
    async def watch_deals(callback: CallbackQuery, button: Button, manager: DialogManager):
        proposed_by = manager.dialog_data.get("proposed_for")

        deals: TasksList = await Tasks().get_user_proposed_tasks(
            proposed_by=proposed_by,
            user_id=callback.from_user.id
        ).do_request()

        manager.dialog_data["returned_deals"] = deals

        await manager.switch_to(state=DealsGroup.watch_deals)

    @staticmethod
    @cancel_dialog_wrapper
    async def cancel_dialog(callback: CallbackQuery, button: Button, manager: DialogManager):
        cur_state = manager.dialog_data.get("cur_state")
        return cur_state

    @staticmethod
    @cancel_dialog_wrapper
    async def cancel_subdialog(callback: CallbackQuery, button: Button, manager: DialogManager):
        cur_state = manager.start_data.get("cur_state")
        return cur_state

    @staticmethod
    async def save_deal(callback: CallbackQuery, button: Button, manager: DialogManager):
        executor_id = manager.dialog_data.get("executor_id")
        proposed_by = manager.start_data.get("proposed_by")

        executor: ExecutorModel = await Executors().get_executor_data(executor_id).do_request()

        task = await Tasks().save_task_data(
            client_id=callback.from_user.id,
            executor_id=executor.user_id,
            description=manager.dialog_data.get('desc'),
            price=manager.dialog_data.get('price'),
            subjects=manager.dialog_data.get('subject_title'),
            files=manager.dialog_data.get("docs", []),
            files_type=manager.dialog_data.get("type", []),
            status=TaskStatus.active,
            work_type=manager.dialog_data.get('task_type'),
            proposed_by=proposed_by,
        ).do_request()

        if not isinstance(task, TaskModel):
            await callback.message.answer("Проблеми зі збереженням!")
            return

        await callback.message.answer("Дані успішно збережено! Скоро виконавець отримає ваше повідомлення!")
        await callback.bot.send_message(
            chat_id=manager.dialog_data.get("executor_id"),
            text="🌟 <b>У вас є нові запропоновані угоди!</b> 🌟"
                 "Перевірте їх у розділі <b>‘Угоди’</b> тільки у меню <i>виконавця</i>. "
                 "Не пропустіть цю можливість!",
            parse_mode="HTML"
        )

        await manager.done()
