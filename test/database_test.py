import decimal

from database.crud import get_recent_clients, get_usual_users, save_chat_data, create_transaction_data, get_chat_object, \
    get_similarity_users
import datetime
import asyncio

# print(asyncio.run(
#     get_chat_object(db_chat_id=1)
# ))

# asyncio.run(
#     save_chat_data(
#         client_id=411437789,
#         executor_id=487879269,
#         task_id=2,
#         chat_id=4033820825,
#         group_name='Замовлення №2',
#         invite_link='https://t.me/+UmBGfptmV7NkOTFi',
#         participants_count=10,
#         chat_admin="admin"
#     )
# )


# asyncio.run(
#     create_transaction_data(
#         receiver_id=487879269,
#         sender_id=411437789,
#         task_id=1,
#         amount=decimal.Decimal(23)
#     )
# )

# f = asyncio.run(
#     get_chat_object(
#         chat_id=4039450912
#     )
# )
#
# print(f)
