from typing import Optional, List
from urllib.parse import urlencode

from database_api.base import BaseAPI, HttpMethod, APIListObject
from pydantic import BaseModel
from database_api.components.tasks import TasksList
from database_api.components.users import UserResponseList
import enum


class ProfileStatus(enum.StrEnum):
    created: str = "created"
    accepted: str = "accepted"
    rejected: str = "rejected"


class TaskStatus(enum.StrEnum):
    active: str = "active"
    executing: str = "executing"
    done: str = "done"


class FileType(enum.StrEnum):
    photo: str = "photo"
    document: str = "document"


class ExecutorModel(BaseModel):
    executor_id: int
    user_id: int
    tags: Optional[List[str]] = None
    description: Optional[str] = None
    profile_state: ProfileStatus
    work_examples: List[str]
    work_files_type: List[FileType]

    def __str__(self):
        return f"Номер заявки: {self.executor_id}"


class ExecutorsList(APIListObject):
    list_values: List[ExecutorModel]


class Executors(BaseAPI):
    def __init__(self):
        super().__init__()
        self.component_path = f"{self.base_url}/executors"

    def get_executor_tasks(self, executor_id: int, status: List[TaskStatus]):
        url = f"{self.component_path}/{executor_id}/"
        url = url + "?" + urlencode(query=dict(status=status), doseq=True)
        print(url)
        self.response_model = TasksList
        return self._construct_params(method=HttpMethod.GET, url=url)

    def save_executor_data(self, user_id: int, tags: List[str], description: str,
                           work_examples: Optional[List[str]], work_files_type: Optional[List[FileType]]):
        url = f"{self.component_path}/"

        json = {
            "user_id": user_id,
            "tags": tags,
            "description": description,
            "work_examples": work_examples,
            "work_files_type": work_files_type
        }
        return self._construct_params(method=HttpMethod.POST, url=url, json=json)

    def get_all_executors(self, *args):
        url = f"{self.component_path}/"
        self.response_model = UserResponseList
        return self._construct_params(method=HttpMethod.GET, url=url)

    def get_executor_data(self, user_id: int):
        url = f"{self.component_path}/{user_id}"
        self.response_model = ExecutorModel
        return self._construct_params(method=HttpMethod.GET, url=url)

    def get_executor_applications(self):
        url = f"{self.component_path}/applications/"
        self.response_model = ExecutorsList
        return self._construct_params(method=HttpMethod.GET, url=url)

    def update_executor_status(self, executor_id: int, new_status: ProfileStatus):
        url = f"{self.component_path}/applications/"

        json = {
            "executor_id": executor_id,
            "new_profile_state": new_status
        }
        return self._construct_params(method=HttpMethod.PATCH, url=url, json=json)
