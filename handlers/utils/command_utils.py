from aiogram import types
from aiogram.fsm.context import FSMContext
from keyboards.clients import create_keyboard_client
from keyboards.keyboard_fields import ClientKeyboard

from database.crud import get_user_auth
from handlers.states_handler import ClientDialog

from utils.dialog_texts import auth_text


async def show_menu(message: types.Message, state: FSMContext):
    result = await get_user_auth(message.from_user.id)

    if result:
        await state.set_state(ClientDialog.client_state)
        await message.answer(
            text="<b>Обери наступну дію</b>",
            reply_markup=create_keyboard_client(),
            parse_mode="HTML"
        )
    else:
        kbd = [
            [
                types.KeyboardButton(text=ClientKeyboard.send_number, request_contact=True),
                types.KeyboardButton(text=ClientKeyboard.cancel)
            ]
        ]
        await message.answer(
            text=auth_text,
            reply_markup=types.ReplyKeyboardMarkup(keyboard=kbd, resize_keyboard=True),
            parse_mode="HTML"
        )
