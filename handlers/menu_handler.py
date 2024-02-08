import random

from aiogram.filters import Command
from aiogram import types, F, Bot
from aiogram.enums import ChatType
from aiogram.fsm.context import FSMContext
from aiogram.dispatcher.router import Router
from aiogram_dialog.dialog import DialogManager

from handlers.utils.command_utils import show_menu

from database_api.components.tasks import Tasks, TaskModel, PropositionBy, TaskStatus

from utils.channel_creating import TELEGRAM_USER
from utils.channel_creating import creating_chat_for_users

from handlers.states_handler import ClientDialog
from keyboards.clients import create_keyboard_client
from handlers.utils.start_action_handler import ProcessOrder
from aiogram.methods.delete_message import DeleteMessage
from utils.instructions import get_client_instructions
from handlers.utils.unused_chats_utils import check_existence_and_create_new_deal

menu_router = Router()
menu_router.message.filter(F.chat.type.in_({ChatType.PRIVATE}))


@menu_router.message(Command("menu"))
async def cmd_menu(message: types.Message, state: FSMContext, dialog_manager: DialogManager):
    await show_menu(message, state)


@menu_router.message(
    F.text.contains("🥳"),
)
async def get_client_menu(message: types.Message, state: FSMContext):
    await state.set_state(ClientDialog.client_state)

    await message.answer(
        text="Переходимо на профіль замовника",
        reply_markup=create_keyboard_client()
    )


@menu_router.message(
    F.text.contains("❗"),
    ClientDialog.client_state
)
async def get_instructions_client(message: types.Message, state: FSMContext):
    await message.answer(
        text=get_client_instructions()
    )


@menu_router.callback_query(
    F.data.contains("take_order")
)
async def handle_taking_order(callback: types.CallbackQuery, bot: Bot, dialog_manager: DialogManager):
    action, task_id = callback.data.split("-")
    processor = ProcessOrder(
        task_id=int(task_id),
        dialog_manager=dialog_manager,
        callback=callback
    )

    await processor.process_action()
    await bot(
        DeleteMessage(
            message_id=int(callback.message.message_id),
            chat_id=callback.message.chat.id
        )
    )
    await callback.answer()


@menu_router.callback_query(
    F.data.contains("create-chat")
)
async def create_chat(callback: types.CallbackQuery, bot: Bot, dialog_manager: DialogManager):
    action, client_id, executor_id, task_id, executor_username = callback.data.split("|")

    task: TaskModel = await Tasks().get_task_data(int(task_id)).do_request()
    if task.proposed_by != PropositionBy.public:
        await Tasks().update_task_status(task.task_id, TaskStatus.executing)

    try:
        return await check_existence_and_create_new_deal(
            client_id=int(client_id),
            task_id=int(task_id),
            executor_id=int(executor_id),
            callback=callback,
            bot=bot
        )

    except ValueError as err:
        print(err)
        print("There are no free chats")

    chat_admin = random.choice(TELEGRAM_USER)

    await creating_chat_for_users(
        client_id=int(client_id),
        executor_id=int(executor_id),
        chat_admin=chat_admin,
        task_id=int(task_id),
        callback=callback,
        bot=bot
    )


@menu_router.callback_query(
    F.data.startswith("deal_minus")
)
async def reject_proposed_deal(callback: types.CallbackQuery, bot: Bot, dialog_manager: DialogManager):
    action, task_id, client_id, executor_id = callback.data.split("|")

    task: TaskModel = await Tasks().get_task_data(int(task_id)).do_request()

    if task.proposed_by == PropositionBy.client:
        await bot.send_message(
            chat_id=int(client_id),
            text=f"Виконавець відмовився від вашого замовлення!\n\nІнформаця по замовленню:\n\n"
                 f"{task.create_task_summary()}"
        )
    elif task.proposed_by == PropositionBy.executor:
        await bot.send_message(
            chat_id=int(executor_id),
            text=f"Клієнт відмовився від вашої пропозиції!\n\nІнформаця по замовленню:\n\n"
                 f"{task.create_task_summary()}"
        )

    await Tasks().update_task_status(
        task_id=task.task_id,
        new_task_status=TaskStatus.done
    ).do_request()

    await callback.answer()
    await bot.delete_message(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id
    )
