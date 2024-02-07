import os
import sys
from typing import Tuple, List, Set, Dict, Generic

import redis.asyncio as redis
from redis.asyncio.client import Pipeline
from datetime import datetime, timedelta
import json
from database_api.components.tasks import FileType

from aiogram.types import Message
from handlers_chatbot.utils.input_message import ChooseJsonMessage
from dotenv import load_dotenv

load_dotenv()


class SessionStatus:
    active: str = "active"
    deactivated: str = "deactivated"


REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_DB = os.getenv("REDIS_DB")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

if not all([REDIS_HOST, REDIS_DB, REDIS_PORT]):
    print("You have to specify params for REDIS")
    sys.exit(1)

REDIS_URL = f"redis://{REDIS_HOST}/{REDIS_DB}"
if REDIS_PASSWORD:
    REDIS_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}/{REDIS_DB}"


def construct_session_key(client_id: int, db_chat_id: int) -> str:
    return f"session:{client_id}:{db_chat_id}"


def wrapper_for_redis_conn(func):
    async def decorator_function(*args, **kwargs):
        r = await redis.from_url(REDIS_URL)
        async with r.pipeline(transaction=True) as pipe:
            res = await func(*args, **kwargs, pipe=pipe)

        return res

    return decorator_function


@wrapper_for_redis_conn
async def set_notification_time(db_chat_id: int, pipe: Pipeline):
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


@wrapper_for_redis_conn
async def is_session_active(session_key, pipe: Pipeline):
    res = await pipe.get(session_key).execute()
    print(f"Result from is_session_active: {res[0].decode()}")
    print(res[0].decode() == SessionStatus.active)
    return res[0].decode() == SessionStatus.active


@wrapper_for_redis_conn
async def store_message_in_redis(session_key, message: Message, pipe: Pipeline):
    message_data = {
        "type": message.content_type,
        "content": message.model_dump_json(exclude_none=True, indent=4),
        "from_user_id": message.from_user.id
    }
    print(message_data)

    new_session_key = session_key + ":messages"
    print(f"Hello from storing data: {new_session_key}")
    print(message_data)
    await pipe.rpush(new_session_key, json.dumps(message_data)).execute()


@wrapper_for_redis_conn
async def send_stored_messages(session_key, bot, chat_id, pipe: Pipeline, ):
    key = session_key + ":messages"
    length_of_push = await pipe.llen(key).execute()
    length_of_push = length_of_push[0]

    try:
        while length_of_push > 0:
            message_data_json = await pipe.lpop(key).execute()
            message_data = json.loads(message_data_json[0])
            print(message_data)
            length_of_push -= 1
            content_data = json.loads(message_data.get("content"))

            res = ChooseJsonMessage(content_type=message_data.get("type"))
            handler = res.choose_handler()

            await handler(message_data=content_data, bot=bot).send_message(chat_id=chat_id)

    except Exception as err:
        print("We are in the execpetion of send_stored_messages:\n")
        print(err)
        await deactivate_session(session_key)


@wrapper_for_redis_conn
async def activate_session(session_key, pipe: Pipeline):
    await pipe.set(session_key, SessionStatus.active).execute()
    print("Activated session")


@wrapper_for_redis_conn
async def deactivate_session(session_key, pipe: Pipeline):
    await pipe.set(session_key, SessionStatus.deactivated).execute()
    print("Deactivated session")


@wrapper_for_redis_conn
async def deactivate_all_unused_sessions(session_key: str, client_id: int, pipe: Pipeline):
    pattern_scanning = f"session:{client_id}:*[0-9]"

    res = await pipe.scan(cursor=0, match=pattern_scanning).execute()
    cursor, keys = res[0]

    for key in keys:
        if key.decode() != session_key:
            await pipe.set(key.decode(), SessionStatus.deactivated).execute()


@wrapper_for_redis_conn
async def save_files_ids(unique_id: str, file_id: str, file_type: FileType, pipe: Pipeline):
    await pipe.rpush(unique_id, file_id, file_type).execute()


@wrapper_for_redis_conn
async def get_files_ids(unique_id: str, pipe: Pipeline) -> Tuple[list, list]:
    length_stack = await pipe.llen(unique_id).execute()
    length_stack = length_stack[0]

    file_type = []
    file_id = []

    for ind in range(length_stack):
        data = await pipe.rpop(unique_id).execute()
        if ind % 2 == 0:
            file_type.append(data[0].decode())
        else:
            file_id.append(data[0].decode())

    return file_type, file_id
