import abc
from pprint import pprint

from aiogram import Bot
from aiogram.types import Message
from aiogram.enums import ContentType

import json
from aiogram.types.reply_parameters import ReplyParameters


class ContentHandler(abc.ABC):
    def __init__(self, message: Message, bot: Bot):
        self.message = message
        self.bot = bot
        self.reply_params = None
        if message.reply_to_message:
            self.reply_params = ReplyParameters(
                message_id=message.reply_to_message.message_id,
                chat_id=message.chat.id
            )

    @abc.abstractmethod
    async def handle_message(self, receiver_id):
        pass


class TextHandler(ContentHandler):
    async def handle_message(self, receiver_id):
        text = self.message.text
        await self.bot.send_message(
            chat_id=receiver_id,
            text=text,
            reply_parameters=self.reply_params
        )


class PhotoHandler(ContentHandler):
    async def handle_message(self, receiver_id):
        photo = self.message.photo
        await self.bot.send_photo(
            chat_id=receiver_id,
            photo=photo[0].file_id,
            reply_parameters=self.reply_params
        )


class DocumentHandler(ContentHandler):
    async def handle_message(self, receiver_id):
        doc = self.message.document
        await self.bot.send_document(
            chat_id=receiver_id,
            document=doc.file_id,
            reply_parameters=self.reply_params
        )


class AudioHandler(ContentHandler):
    async def handle_message(self, receiver_id):
        audio = self.message.audio
        await self.bot.send_audio(
            chat_id=receiver_id,
            audio=audio.file_id,
            reply_parameters=self.reply_params
        )


class VoiceHandler(ContentHandler):
    async def handle_message(self, receiver_id):
        voice = self.message.voice
        await self.bot.send_voice(
            chat_id=receiver_id,
            voice=voice.file_id,
            reply_parameters=self.reply_params
        )


class StickerHandler(ContentHandler):
    async def handle_message(self, receiver_id):
        sticker = self.message.sticker
        await self.bot.send_sticker(
            chat_id=receiver_id,
            sticker=sticker.file_id,
            reply_parameters=self.reply_params
        )


class VideoHandler(ContentHandler):
    async def handle_message(self, receiver_id):
        video = self.message.video
        await self.bot.send_video(
            chat_id=receiver_id,
            video=video.file_id,
            reply_parameters=self.reply_params
        )


class UnknownTypeHandler(ContentHandler):
    async def handle_message(self, receiver_id=None):
        await self.message.answer(
            text="Невідомі ввідні дані! Це повідомлення не буде переслано користувачу"
        )


class ChooseMessageHandler:
    def __init__(self, content_type):
        self.content_type = content_type

    def choose(self):
        print(f"ChooseMessageHandler: {self.content_type}")
        if self.content_type == ContentType.TEXT:
            return TextHandler
        elif self.content_type == ContentType.PHOTO:
            return PhotoHandler
        elif self.content_type == ContentType.DOCUMENT:
            return DocumentHandler
        elif self.content_type == ContentType.AUDIO:
            return AudioHandler
        elif self.content_type == ContentType.VOICE:
            return VoiceHandler
        elif self.content_type == ContentType.STICKER:
            return StickerHandler
        elif self.content_type == ContentType.VIDEO:
            return VideoHandler
        else:
            return UnknownTypeHandler


class JsonMessage(abc.ABC):
    def __init__(self, message_data: dict, bot: Bot):
        self.message_data = message_data
        self.bot = bot
        self.reply_params = None
        if message_data.get('reply_to_message'):
            self.reply_params = ReplyParameters(
                message_id=message_data['reply_to_message']['message_id'],
                chat_id=message_data['chat']['id']
            )

    @abc.abstractmethod
    async def send_message(self, chat_id):
        pass


class TextJsonMessage(JsonMessage):
    async def send_message(self, chat_id):
        await self.bot.send_message(
            chat_id=chat_id,
            text=self.message_data["text"],
            reply_parameters=self.reply_params
        )


class PhotoJsonMessage(JsonMessage):
    async def send_message(self, chat_id):
        await self.bot.send_photo(
            chat_id=chat_id,
            photo=self.message_data["photo"][0]["file_id"],
            reply_parameters=self.reply_params
        )


class DocumentJsonMessage(JsonMessage):
    async def send_message(self, chat_id):
        print("Bad docs!")

        await self.bot.send_document(
            chat_id=chat_id,
            document=self.message_data["document"]["file_id"],
            reply_parameters=self.reply_params
        )


class AudioJsonMessage(JsonMessage):
    async def send_message(self, chat_id):
        print("Bad audio!")
        await self.bot.send_audio(
            chat_id=chat_id,
            audio=self.message_data["audio"]["file_id"],
            reply_parameters=self.reply_params
        )


class VoiceJsonMessage(JsonMessage):
    async def send_message(self, chat_id):
        print("Bad voice!")

        await self.bot.send_voice(
            chat_id=chat_id,
            voice=self.message_data["voice"]["file_id"],
            reply_parameters=self.reply_params
        )


class StickerJsonMessage(JsonMessage):
    async def send_message(self, chat_id):
        await self.bot.send_sticker(
            chat_id=chat_id,
            sticker=self.message_data["sticker"]["file_id"],
            reply_parameters=self.reply_params
        )


class VideoJsonMessage(JsonMessage):
    async def send_message(self, chat_id):
        print("Bad video!")

        await self.bot.send_video(
            chat_id=chat_id,
            video=self.message_data["video"]["file_id"],
            reply_parameters=self.reply_params
        )


class ChooseJsonMessage:
    def __init__(self, content_type):
        self.content_type = content_type

    def choose_handler(self):
        print(f"ChooseJsonMessage: {self.content_type}")
        if self.content_type == ContentType.TEXT.value or self.content_type == ContentType.TEXT:
            return TextJsonMessage
        elif self.content_type == ContentType.PHOTO.value or self.content_type == ContentType.PHOTO:
            return PhotoJsonMessage
        elif self.content_type == ContentType.DOCUMENT.value or self.content_type == ContentType.DOCUMENT:
            return DocumentJsonMessage
        elif self.content_type == ContentType.AUDIO.value or self.content_type == ContentType.AUDIO:
            return AudioJsonMessage
        elif self.content_type == ContentType.VOICE.value or self.content_type == ContentType.VOICE:
            return VoiceJsonMessage
        elif self.content_type == ContentType.STICKER.value or self.content_type == ContentType.STICKER:
            return StickerJsonMessage
        elif self.content_type == ContentType.VIDEO.value or self.content_type == ContentType.VIDEO:
            return VideoJsonMessage
