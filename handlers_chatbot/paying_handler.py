import decimal

from aiogram import F, types, Bot
from aiogram.enums import ChatType
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from aiogram.filters.command import Command, CommandObject
from aiogram.dispatcher.router import Router
from aiogram_dialog.dialog import DialogManager
from aiogram_dialog.api.entities import StartMode

from handlers_chatbot.paying_order.window_dialogs import create_offer_dialog
from handlers_chatbot.paying_order.window_states import PriceOffer, PriceOfferAccept
from handlers.utils.start_action_handler import change_message_status
from database.crud import get_chat_object, create_transaction_data, get_task, check_successful_payment, \
    accept_done_offer
from database.models import Chat, TaskStatus, Task
from utils.dialog_texts import paying_text_accepted
from utils.channel_creating import edit_telegram_message
from sqlalchemy.exc import IntegrityError

paying_router = Router()

paying_router.message.filter(F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL}))
paying_router.include_routers(*create_offer_dialog())


def create_accept_offer_msg(task_id: int, transaction_id: int, amount: int, receiver_id: int):
    builder = InlineKeyboardBuilder()

    builder.add(
        InlineKeyboardButton(
            text="Підтвердити виконання",
            callback_data=f"accept_offer|{transaction_id}|{task_id}|{amount}|{receiver_id}"
        )
    )

    return builder.as_markup()


@paying_router.message(
    Command("pay")
)
async def create_payment(message: types.Message, dialog_manager: DialogManager):
    chat_db_id = message.chat.title.split("№")[-1]

    print("Hello paying chat")
    chat_obj: Chat = await get_chat_object(db_chat_id=int(chat_db_id))

    task: Task = await get_task(chat_obj.task_id)

    if message.from_user.id != chat_obj.executor_id:
        return await message.answer("Ціну може пропонувати тільки виконавець!")

    is_payed = await check_successful_payment(
        task_id=chat_obj.task_id,
        sender_id=chat_obj.client_id,
        receiver_id=chat_obj.executor_id
    )

    print(is_payed)

    if is_payed:
        return await message.answer("Це завдання оплачено! Щоб здійснити оплату ще раз зробіть нове замовлення!")

    if task.executor_id != chat_obj.executor_id or task.executor_id is not None:
        return await message.answer("Це завдання вже виконується іншим виконавцем!")

    await dialog_manager.start(
        state=PriceOffer.offer_price,
        mode=StartMode.RESET_STACK,
        data={
            "chat_obj": chat_obj
        }
    )


@paying_router.callback_query(
    F.data.startswith("offer")
)
async def process_offer(callback: types.CallbackQuery, bot: Bot):
    action, chat_id, task_id, price = callback.data.split("|")

    chat: Chat = await get_chat_object(db_chat_id=int(chat_id))

    try:

        transaction = await create_transaction_data(
            receiver_id=chat.executor_id,
            sender_id=chat.client_id,
            amount=decimal.Decimal(price),
            task_id=int(task_id)
        )

    except ValueError as error:
        print(error)
        return await callback.answer(text="Неможливо зараз здійснити транзакцію!")

    await callback.answer()

    await bot.delete_message(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id
    )

    await bot.send_message(
        chat_id=callback.from_user.id,
        text="Дане повідомлення призначення для того, щоб підтвердити успішне виконання завдання виконавцем."
             "Зараз гроші знаходяться на утриманні, з Вашого балансу вони зняті, але ще не перераховані виконавцю!"
             "При будь-яких проблемах звертайтеся до адміна @{нік_адміна} або пишіть тікет за командою"
             "/ticket",
        reply_markup=create_accept_offer_msg(
            task_id=task_id,
            transaction_id=transaction.transaction_id,
            receiver_id=transaction.receiver_id,
            amount=transaction.amount
        )
    )

    await edit_telegram_message(
        task_id=int(task_id),
        new_status=TaskStatus.executing,
        is_active=False
    )


@paying_router.callback_query(
    F.data.startswith("reject")
)
async def process_reject(callback: types.CallbackQuery, bot: Bot):
    action, chat_id, task_id, price = callback.data.split("|")
    print("Reject")

    await bot.send_message(
        chat_id=int(chat_id),
        text="<b>Клієнт відмовився від запропонованої вами ціни!</b>\n\nСпробуйте домовитися знову!",
        parse_mode="HTML"
    )

    await callback.answer()
    await bot.delete_message(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id
    )


@paying_router.callback_query(
    F.data.startswith("accept_offer")
)
async def accept_offer(callback: types.CallbackQuery, bot: Bot):
    action, transaction_id, task_id, amount, receiver_id = callback.data.split("|")

    try:

        await accept_done_offer(
            transaction_id=int(transaction_id),
            task_id=int(task_id),
            receiver_id=int(receiver_id),
            amount=decimal.Decimal(amount)
        )

    except IntegrityError as err:
        print(err)
        return await callback.answer("Неможливо зараз обробити цей запит! Можливо у вас не вистачає коштів!")

    await callback.answer()

    await bot.delete_message(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id
    )

    await edit_telegram_message(
        task_id=int(task_id),
        new_status=TaskStatus.done,
        is_active=False
    )
