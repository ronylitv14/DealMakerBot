from aiogram import types, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command, CommandObject, CommandStart
from aiogram.enums import ChatType, ContentType
from aiogram.dispatcher.router import Router

from handlers_chatbot.utils.redis_interaction import store_message_in_redis, send_stored_messages, is_session_active, \
    deactivate_session, activate_session
from database.crud import get_chat_object

chat_router = Router()
chat_router.message.filter(F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}))


def get_chat_wrapper(func):
    async def decorator(message: types.Message, bot: Bot, state: FSMContext, *args, **kwargs):
        deal_id = message.chat.title.split("№")[-1]

        storage_data = await state.get_data()
        chat_obj = storage_data.get(deal_id)

        if not chat_obj:
            chat_obj = await get_chat_object(db_chat_id=int(deal_id))
            await state.set_data({deal_id: chat_obj})

        if message.from_user.id not in [chat_obj.client_id, chat_obj.executor_id]:
            return await message.answer("Ваше повідомлення не буде переслано нікуди так як ви не є безспосередньо"
                                        " виконавцем чи клієнтом!")
        print(chat_obj.client_id)
        session_key = f"session:{chat_obj.client_id}:{chat_obj.id}"
        is_active = await is_session_active(session_key)
        print(f"\nChat handler\n\nSession is active: {is_active}\n")
        if not is_active:
            await store_message_in_redis(session_key, message=message)
            print("saving message from executor\n\n")
            return

        print("Sending uptime new messages!")
        await func(message, bot, state, chat_obj=chat_obj, **kwargs)
        return

    return decorator


@chat_router.message(
    F.text
)
@get_chat_wrapper
async def send_text_message(message: types.Message, bot: Bot, state: FSMContext, *args, **kwargs):
    if message.text.startswith("/"):
        return

    chat_obj = kwargs.get("chat_obj")

    if message.from_user.id == chat_obj.executor_id:
        await bot.send_message(
            chat_id=chat_obj.client_id,
            text=message.text
        )


@chat_router.message(
    F.photo
)
@get_chat_wrapper
async def send_photo_message(message: types.Message, bot: Bot, state: FSMContext, *args, **kwargs):
    chat_obj = kwargs.get("chat_obj")

    if message.from_user.id == chat_obj.executor_id:
        await bot.send_photo(
            chat_id=chat_obj.client_id,
            photo=message.photo[0].file_id
        )


@chat_router.message(
    F.document
)
@get_chat_wrapper
async def send_document_message(message: types.Message, bot: Bot, state: FSMContext, *args, **kwargs):
    chat_obj = kwargs.get("chat_obj")

    if message.from_user.id == chat_obj.executor_id:
        await bot.send_document(
            chat_id=chat_obj.client_id,
            document=message.document.file_id
        )


@chat_router.message(
    F.audio
)
@get_chat_wrapper
async def send_audio_message(message: types.Message, bot: Bot, state: FSMContext, *args, **kwargs):
    chat_obj = kwargs.get("chat_obj")

    if message.from_user.id == chat_obj.executor_id:
        await bot.send_audio(
            chat_id=chat_obj.client_id,
            audio=message.audio.file_id
        )


@chat_router.message(
    F.voice
)
@get_chat_wrapper
async def send_voice_message(message: types.Message, bot: Bot, state: FSMContext, *args, **kwargs):
    chat_obj = kwargs.get("chat_obj")

    if message.from_user.id == chat_obj.executor_id:
        await bot.send_voice(
            chat_id=chat_obj.client_id,
            voice=message.voice.file_id
        )


@chat_router.message(
    F.sticker
)
@get_chat_wrapper
async def send_sticker_message(message: types.Message, bot: Bot, state: FSMContext, *args, **kwargs):
    chat_obj = kwargs.get("chat_obj")

    if message.from_user.id == chat_obj.executor_id:
        await bot.send_sticker(
            chat_id=chat_obj.client_id,
            sticker=message.sticker.file_id
        )


@chat_router.message(
    F.video
)
@get_chat_wrapper
async def send_sticker_message(message: types.Message, bot: Bot, state: FSMContext, *args, **kwargs):
    chat_obj = kwargs.get("chat_obj")

    if message.from_user.id == chat_obj.executor_id:
        await bot.send_video(
            chat_id=chat_obj.client_id,
            video=message.video.file_id
        )


@chat_router.message(
    F.contact,
    F.location,
    F.venue,
    F.story,
    F.user_shared,
    F.chat_shared,
    F.connected_website
)
@get_chat_wrapper
async def send_sticker_message(message: types.Message, bot: Bot, state: FSMContext, *args, **kwargs):
    chat_obj = kwargs.get("chat_obj")

    if message.from_user.id == chat_obj.executor_id:
        await message.answer(
            text="Даний тип повідомелння заборонено на нашій площадці!\n\n"
                 "При повторному виявлені таких дій Вас може бути заблоковано адміністратором!"
        )
