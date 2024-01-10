import datetime
import decimal
from typing import Optional, List
from urllib.parse import urlencode
from pydantic import BaseModel, ConfigDict
from database_api.base import BaseAPI, HttpMethod


class GroupMessageResponse(BaseModel):
    group_message_id: int
    task_id: int
    message_text: str
    has_files: bool
    date_added: datetime.datetime


class GroupMessages(BaseAPI):
    def __init__(self):
        super().__init__()
        self.component_path = f"{self.base_url}/group-messages"

    def save_group_message(self, group_message_id: int, task_id: int, message_text: str, has_files: bool):
        url = f"{self.component_path}/"

        json = {
            "group_message_id": group_message_id,
            "task_id": task_id,
            "message_text": message_text,
            "has_files": has_files
        }
        return self.construct_params(method=HttpMethod.POST, url=url, json=json)

    def get_group_message_by_task(self, task_id: int):
        url = f"{self.component_path}/{task_id}"
        self.response_model = GroupMessageResponse
        return self.construct_params(method=HttpMethod.GET, url=url)
