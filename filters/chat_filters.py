from aiogram.types import Message, ChatMemberOwner, ChatMemberAdministrator
from typing import Any, Union, Dict

from aiogram.filters import BaseFilter


class IsNotAdmin(BaseFilter):
    async def __call__(self, message: Message, *args: Any, **kwargs: Any) -> Union[bool, Dict[str, Any]]:
        members = await message.bot.get_chat_administrators(chat_id=message.chat.id)
        print(members)
        print("Hello")
        for member in members:
            if isinstance(member, (ChatMemberAdministrator, ChatMemberOwner)):
                return False

        print("Have true")
        return True
