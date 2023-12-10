from aiogram.filters import BaseFilter
from aiogram.types.message import ContentType
from aiogram.types import Message
from typing import Union


class InputFilter(BaseFilter):
    def __init__(self, input_type: Union[str, list]):
        self.input_type = input_type

    async def __call__(self, message: Message,  *args, **kwargs):
        if isinstance(self.input_type, str):
            return message.content_type == self.input_type
        else:
            return message.content_type in self.input_type

