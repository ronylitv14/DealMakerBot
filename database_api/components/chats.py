import datetime
from typing import Optional, List, Iterator
from urllib.parse import urlencode
from database_api.base import BaseAPI, HttpMethod, APIListObject
from database_api.components.users import UserResponseList
from aiogram.enums import ChatType
from pydantic import BaseModel, ConfigDict


class ChatModel(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    id: int
    chat_id: int
    supergroup_id: Optional[int] = None
    task_id: Optional[int] = None
    executor_id: int
    client_id: int
    group_name: str
    chat_type: ChatType
    chat_admin: str
    date_created: datetime.datetime
    active: bool
    is_payed: bool
    payment_data: Optional[datetime.datetime] = None
    participants_count: Optional[int] = None
    invite_link: Optional[str] = None

    def __str__(self):
        return f"Номер чату: {self.id}, Номер замовлення: {self.task_id}"


class ChatsList(APIListObject):
    list_values: List[ChatModel]


class Chats(BaseAPI):
    def __init__(self):
        super().__init__()
        self.component_path = f"{self.base_url}/chats"

    def save_chat_data(self, chat_id: int, task_id: int, group_name: str, invite_link: str, participants_count: int,
                       client_id: int, executor_id: int, chat_admin: str, supergroup_id: Optional[int] = None):
        url = f"{self.component_path}/"
        json = {
            "chat_id": chat_id,
            "task_id": task_id,
            "group_name": group_name,
            "invite_link": invite_link,
            "participants_count": participants_count,
            "client_id": client_id,
            "executor_id": executor_id,
            "chat_admin": chat_admin,
            "supergroup_id": supergroup_id
        }
        self.response_model = ChatModel
        return self._construct_params(method=HttpMethod.POST, url=url, json=json)

    def get_chat_data(self, chat_id: Optional[int] = None, db_chat_id: Optional[int] = None,
                      supergroup_id: Optional[int] = None):
        ids_data = dict(chat_id=chat_id, db_chat_id=db_chat_id, supergroup_id=supergroup_id)

        ids_data = {k: v for k, v in ids_data.items() if v is not None}

        path = f"{self.component_path}/"
        url = path + "?" + urlencode(ids_data)
        self.response_model = ChatModel
        return self._construct_params(method=HttpMethod.GET, url=url)

    def get_recent_clients(self, executor_id: int):
        url = f"{self.component_path}/recent-clients/{executor_id}"
        self.response_model = UserResponseList
        return self._construct_params(method=HttpMethod.GET, url=url)

    def get_chats_by_task_id(self, task_id: int):
        url = f"{self.component_path}/chats-by-task/{task_id}"
        self.response_model = ChatsList
        return self._construct_params(method=HttpMethod.GET, url=url)

    def update_chat_type(self, chat_type: ChatType, supergroup_id: Optional[int] = None,
                         db_chat_id: Optional[int] = None):
        if supergroup_id is None and db_chat_id is None:
            raise ValueError("None of id`s for chat were specified!")

        url = f"{self.component_path}/type/"
        json = {
            "chat_type": chat_type,
            "supergroup_id": supergroup_id,
            "db_chat_id": db_chat_id
        }
        return self._construct_params(method=HttpMethod.PATCH, url=url, json=json)

    def get_all_user_chats(self, client_id: int):
        url = f"{self.component_path}/user/{client_id}"
        self.response_model = ChatsList
        return self._construct_params(method=HttpMethod.GET, url=url)

    def update_group_title(self, db_chat_id: int, group_name: str):
        url = f"{self.component_path}/group-title/"
        json = {
            "db_chat_id": db_chat_id,
            "group_name": group_name
        }
        return self._construct_params(method=HttpMethod.PATCH, url=url, json=json)

    def get_all_unused_chats(self):
        url = f"{self.component_path}/unused/"
        self.response_model = ChatsList
        return self._construct_params(method=HttpMethod.GET, url=url)

    def update_chat_field(
            self,
            db_chat_id: int,
            group_name: Optional[str] = None,
            participants_count: Optional[int] = None,
            active: Optional[bool] = None,
            in_use: Optional[bool]= None
    ):
        url = f"{self.component_path}/{db_chat_id}"

        json = {
            "active": active,
            "group_name": group_name,
            "participants_count": participants_count,
            "in_use": in_use
        }

        return self._construct_params(method=HttpMethod.PATCH, url=url, json=json)

    def check_chat_existence(
            self,
            task_id: int,
            executor_id: int,
            client_id: int
    ):
        url = f"{self.component_path}/exists/"

        ids_data = {
            "task_id": task_id,
            "executor_id": executor_id,
            "client_id": client_id
        }

        url = url + "?" + urlencode(ids_data)
        return self._construct_params(method=HttpMethod.GET, url=url)
