from aiogram.types import CallbackQuery
from aiogram_dialog.dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.api.entities import StartMode

from handlers.deals.window_state import CreateDeal, DealsGroup
from handlers.states_handler import ClientDialog, ExecutorDialog
from keyboards.clients import create_keyboard_client
from keyboards.executors import create_keyboard_executor

from database.crud import save_task_to_db, get_executor, get_proposed_deals
from database.models import TaskStatus, PropositionBy


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
        # manager.dialog_data["subject_title"] = []

        cur_state = manager.dialog_data.get("cur_state")
        state_obj = manager.dialog_data.get("state_obj")

        print(cur_state)
        print(state_obj)
        await manager.start(
            state=CreateDeal.choose_nickname,
            data={
                "user_id": callback.from_user.id,
                "cur_state": cur_state,
                "state_obj": state_obj
            }
        )

    @staticmethod
    async def watch_deals(callback: CallbackQuery, button: Button, manager: DialogManager):
        proposed_by = manager.dialog_data.get("proposed_by")

        deals = await get_proposed_deals(
            proposed_by=proposed_by,
            user_id=callback.from_user.id
        )

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
        cur_state = manager.start_data.get("cur_state")

        executor_id = manager.dialog_data.get("executor_id")

        executor = await get_executor(executor_id)

        await save_task_to_db(
            client_id=callback.from_user.id,
            executor_id=executor.executor_id,
            description=manager.dialog_data.get('desc'),
            price=manager.dialog_data.get('price'),
            deadline=manager.dialog_data.get('date'),
            subjects=manager.dialog_data.get('subject_title'),
            files=manager.dialog_data.get("docs", []),
            files_type=manager.dialog_data.get("type", []),
            status=TaskStatus.active,
            work_type=manager.dialog_data.get('task_type'),
            proposed_by=PropositionBy.client if cur_state == ClientDialog.client_state else PropositionBy.executor,
        )

        await callback.message.answer("Дані успішно збережено! Скоро виконавець отримає ваше повідомлення!")
        await callback.bot.send_message(
            chat_id=manager.dialog_data.get("executor_id"),
            text="<b>У вас є нові запропоновані угоди! Перевірте їх у розділі 'Угоди'</b>",
            parse_mode="HTML"
        )

        await manager.done()
