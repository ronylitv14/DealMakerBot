from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from aiogram import Bot


from database_api.components.tasks import TaskModel, Tasks
from database_api.components.chats import ChatModel


def create_accept_offer(chat_id: int, task_id: int, price: int):
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text="Прийняти замовлення",
            callback_data=f"offer|{chat_id}|{task_id}|{price}",

        ),
        InlineKeyboardButton(
            text="Відмовитись",
            callback_data=f"reject|{chat_id}|{task_id}|{price}"
        )
    )

    return builder.as_markup()


class InputCallbacks:
    @staticmethod
    async def process_offer_price(message: Message, widget: MessageInput, manager: DialogManager):
        chat_obj = manager.start_data.get("chat_obj")

        price = message.text

        task: TaskModel = await Tasks().get_task_data(chat_obj['task_id']).do_request()

        try:
            price = int(price)

            if price < 0:
                raise ValueError

            manager.dialog_data["price"] = price
            bot: Bot = message.bot

            await bot.send_message(
                chat_id=chat_obj['client_id'],
                text=f"Ви приймаєте це замовлення?\n\nЗамовлення щодо завдання: {chat_obj['task_id']}\n\n"
                     f"Предмет завдання: {task.subjects}\n\n"
                     f"Опис завдання: \n\n{task.description}\n\n"
                     f"Запропонована ціна: <b>{price} грн</b>",
                reply_markup=create_accept_offer(
                    chat_id=chat_obj['id'],
                    task_id=chat_obj['task_id'],
                    price=price
                ),
                parse_mode="HTML"
            )

            await manager.done()
        except ValueError:
            await message.answer("Неправильно введена сума")


class ButtonCallbacks:
    @staticmethod
    async def accept_price(callback: CallbackQuery, button: Button, manager: DialogManager):
        await callback.answer(text="Ви прийняли ціну!")

    @staticmethod
    async def reject_price(callback: CallbackQuery, button: Button, manager: DialogManager):
        await callback.answer(text="Ви відмовили в ціні")
