import random

from aiogram.filters import Command
from aiogram import types, F, Bot
from aiogram.enums import ChatType
from aiogram.fsm.context import FSMContext
from aiogram.dispatcher.router import Router
from aiogram_dialog.dialog import DialogManager

from handlers.utils.command_utils import show_menu
from database.crud import get_user_auth, save_chat_data, update_group_title, get_task
from database.models import Task, PropositionBy

from .states_handler import ClientDialog
from keyboards.clients import create_keyboard_client
from handlers.utils.start_action_handler import ProcessOrder
from aiogram.methods.delete_message import DeleteMessage
from aiogram_dialog.api.exceptions import UnknownState, UnknownIntent, OutdatedIntent
from middlewares.auth_middelware import InnerAuthMiddleware
from utils.instructions import get_client_instructions
from utils.channel_creating import AdminRights, add_admin_rights, create_channel_with_users, \
    get_chat_invite_link, BOT_URL, send_bot_single_inline_message, CHAT_BOT_URL

menu_router = Router()
menu_router.message.filter(F.chat.type.in_({ChatType.PRIVATE}))


@menu_router.message(Command("menu"))
async def cmd_menu(message: types.Message, state: FSMContext):
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
        message=callback.message,
        task_id=int(task_id),
        dialog_manager=dialog_manager
    )

    await processor.process_action()
    await bot(
        DeleteMessage(
            message_id=int(callback.message.message_id),
            chat_id=callback.message.chat.id
        )
    )
    await callback.answer()


from utils.channel_creating import TELEGRAM_USER, change_chat_title
from utils.channel_creating import creating_chat_for_users


@menu_router.callback_query(
    F.data.contains("create-chat")
)
async def create_chat(callback: types.CallbackQuery, bot: Bot, dialog_manager: DialogManager):
    action, client_id, executor_id, task_id, executor_username = callback.data.split("|")

    chat_admin = random.choice(TELEGRAM_USER)

    await creating_chat_for_users(
        client_id=int(client_id),
        executor_id=int(executor_id),
        chat_admin=chat_admin,
        task_id=int(task_id),
        callback=callback,
        bot=bot
    )

    # group_name = f"Замовлення №{task_id}"
    #
    # chat_id = await create_channel_with_users(
    #     group_name,
    #     chat_admin,
    #     BOT_URL,
    #     CHAT_BOT_URL
    # )
    #
    # await add_admin_rights(
    #     chat_id=chat_id,
    #     user=BOT_URL,
    #     is_admin=True,
    #     admin_name=chat_admin
    # )
    #
    # await add_admin_rights(
    #     chat_id=chat_id,
    #     user=CHAT_BOT_URL,
    #     is_admin=True,
    #     admin_name=chat_admin
    # )
    #
    # link = await get_chat_invite_link(chat_id=chat_id, admin_name=chat_admin)
    #
    # new_chat = await save_chat_data(
    #     chat_id=chat_id,
    #     invite_link=link,
    #     participants_count=4,
    #     group_name=group_name,
    #     task_id=int(task_id),
    #     executor_id=int(executor_id),
    #     client_id=int(client_id),
    #     chat_admin=chat_admin
    # )
    #
    # if not new_chat:
    #     return await callback.answer("Помилка при створенні чату!")
    #
    # await change_chat_title(
    #     chat_id=new_chat.chat_id,
    #     chat_admin=chat_admin,
    #     chat_title=f"Угода №{new_chat.id}"
    # )
    #
    # await send_bot_single_inline_message(
    #     chat_id=int(client_id),
    #     msg_text="За цим посиланням ви можете перейти до діалогу з виконавцем",
    #     btn_text="Перейти до чату",
    #     url=f"https://t.me/dealmakerchatbot?start=chat-{new_chat.id}",
    #     bot=bot
    # )
    #
    # await send_bot_single_inline_message(
    #     chat_id=int(executor_id),
    #     msg_text="За цим посиланням ви можете перейти до діалогу з клієнтом",
    #     btn_text="Перейти до чату",
    #     url=link,
    #     bot=bot
    # )
    #
    # await callback.answer()
    #
    # await bot(
    #     DeleteMessage(
    #         message_id=int(callback.message.message_id),
    #         chat_id=callback.message.chat.id
    #     )
    # )
    #
    # await update_group_title(
    #     db_chat_id=new_chat.id,
    #     group_name=f"Угода №{new_chat.id}"
    # )


@menu_router.callback_query(
    F.data.startswith("deal_minus")
)
async def reject_proposed_deal(callback: types.CallbackQuery, bot: Bot, dialog_manager: DialogManager):
    task_id, client_id, executor_id = callback.data.split("|")

    task: Task = await get_task(int(task_id))

    if task.proposed_by == PropositionBy.client:
        await bot.send_message(
            chat_id=int(executor_id),
            text="Виконавець відмовився від вашого замовлення! "
        )
    elif task.proposed_by == PropositionBy.executor:
        await bot.send_message(
            chat_id=int(client_id),
            text="Клієнт відмовився від вашої пропозиції!"
        )
