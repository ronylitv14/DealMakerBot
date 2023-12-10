from handlers_chatbot.utils.redis_interaction import store_message_in_redis, send_stored_messages, activate_session, \
    deactivate_session, is_session_active, deactivate_all_unused_sessions

from utils.redis_utils import set_notification_time, compare_notification_time

import asyncio


# async def run_test():
#
#     await activate_session(
#         "session:411437789:10"
#     )
#
#     await activate_session(
#         "session:411437789:1000"
#     )
#
#     await deactivate_all_unused_sessions(
#         "random",
#         411437789
#     )

# async def test_redis():
#     db_chat_id = 5
#
#     # print(await set_notification_time(
#     #     db_chat_id
#     # ))
#
#     print(await compare_notification_time(
#         db_chat_id,
#         1
#     ))

# asyncio.run(test_redis())
# asyncio.run(run_test())
