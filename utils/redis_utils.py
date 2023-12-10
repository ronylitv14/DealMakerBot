import redis.asyncio as redis
from redis.asyncio.client import Pipeline
from datetime import datetime, timedelta
import json

from aiogram.types import Message
from handlers_chatbot.utils.input_message import ChooseJsonMessage


class SessionStatus:
    active: str = "active"
    deactivated: str = "deactivated"


def wrapper_for_redis_conn(func):
    async def decorator_function(*args, **kwargs):
        r = await redis.from_url("redis://localhost/6379::0")
        async with r.pipeline(transaction=True) as pipe:
            res = await func(*args, **kwargs, pipe=pipe)

        return res

    return decorator_function


@wrapper_for_redis_conn
async def set_notification_time(db_chat_id: int,  pipe: Pipeline):
    key = f"notification:{db_chat_id}"
    await pipe.set(key, datetime.utcnow().timestamp()).execute()


@wrapper_for_redis_conn
async def compare_notification_time(db_chat_id: int, compare_time: int, pipe: Pipeline):
    key = f"notification:{db_chat_id}"
    res = await pipe.get(key).execute()
    if res[0] is not None:
        timestamp = float(res[0].decode())

        difference = (datetime.utcnow().timestamp() - timestamp)
        return (difference / 60) > compare_time
    return True

