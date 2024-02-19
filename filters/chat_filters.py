from aiogram.types import Message, ChatMemberOwner, ChatMemberAdministrator
from typing import Any, Union, Dict

from aiogram.filters import BaseFilter


class IsAdmin(BaseFilter):
    async def __call__(self, message: Message, *args: Any, **kwargs: Any) -> Union[bool, Dict[str, Any]]:
        member = message.chat.get_member(message.from_user.id)
        if isinstance(member, (ChatMemberAdministrator, ChatMemberOwner)):
            return True
        return False
