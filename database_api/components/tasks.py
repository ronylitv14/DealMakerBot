import datetime
from typing import Optional, List, Union
from pydantic import BaseModel, ConfigDict
from urllib.parse import urlencode
from database_api.base import BaseAPI, HttpMethod, APIListObject
from database_api.components.users import UserResponse
import enum


class TaskStatus(enum.StrEnum):
    active: str = "active"
    executing: str = "executing"
    done: str = "done"


class FileType(enum.StrEnum):
    photo: str = "photo"
    document: str = "document"


class PropositionBy(enum.StrEnum):
    executor: str = "executor"
    client: str = "client"
    public: str = "public"


class UserStatus(enum.StrEnum):
    default: str = "default_user"
    admin: str = "admin"
    superuser: str = "superuser"


class UserType(enum.Enum):
    client: str = "Client"
    executor: str = "Executor"


class TaskModel(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    task_id: int
    executor_id: Optional[int] = None
    client_id: Optional[int] = None
    status: TaskStatus
    price: str
    date_added: Optional[datetime.datetime] = None
    deadline: Optional[datetime.date] = None
    proposed_by: PropositionBy
    files: Optional[List[str]] = None
    files_type: Optional[List[FileType]] = None
    description: Optional[str] = None
    subjects: List[str]
    work_type: List[str]

    def __str__(self):
        str_subjects = "-".join(self.subjects)
        return f"Замовлення #{self.task_id}, {str_subjects}"

    def create_task_summary(self):
        str_subjects = "#" + " #".join([task_subject.replace(" ", "_") for task_subject in self.subjects])
        str_work_type = "#" + " #".join([task_type.replace(" ", "_") for task_type in self.work_type])
        return f"Номер замовлення: {self.task_id}\nПредмет(и): {str_subjects}\nВид роботи: {str_work_type}\n\nОпис завдання:\n{self.description}"


class TasksList(APIListObject):
    list_values: List[TaskModel]


class Tasks(BaseAPI):
    def __init__(self):
        super().__init__()
        self.component_path = f"{self.base_url}/tasks"

    def save_task_data(self, client_id: int, status: TaskStatus, price: str, subjects: List[str],
                       work_type: List[str], executor_id: Optional[int] = None,
                       proposed_by: PropositionBy = PropositionBy.public,
                       files: Optional[List[str]] = None, files_type: Optional[List[FileType]] = None,
                       description: Optional[str] = None,
                       deadline: Union[datetime.date, str, None] = datetime.date.today()):
        url = f"{self.component_path}/"
        json = {
            "client_id": client_id,
            "status": status,
            "price": price,
            "subjects": subjects,
            "work_type": work_type,
            "deadline": deadline if isinstance(deadline, str) else str(deadline),
            "files": files,
            "files_type": files_type,
            "description": description,
            "proposed_by": proposed_by,
            "executor_id": executor_id
        }
        self.response_model = TaskModel
        return self._construct_params(method=HttpMethod.POST, url=url, json=json)

    def get_all_user_tasks(self, user_id: int, user_type: UserType, task_status: List[TaskStatus],
                           task_id: Optional[int] = None):
        url = f"{self.component_path}/"
        query_params = dict(user_id=user_id, user_type=user_type, task_status=task_status, task_id=task_id)
        if task_id is None:
            query_params = dict(user_id=user_id, user_type=user_type, task_status=task_status)

        url = url + "?" + urlencode(query_params, doseq=True)
        self.response_model = TasksList
        return self._construct_params(method=HttpMethod.GET, url=url)

    def update_task_status(self, task_id: int, new_task_status: TaskStatus):
        url = f"{self.component_path}/status/{task_id}"
        json = {
            "status": new_task_status
        }
        return self._construct_params(method=HttpMethod.PATCH, url=url, json=json)

    def get_task_data(self, task_id: int):
        url = f"{self.component_path}/{task_id}"
        self.response_model = TaskModel
        return self._construct_params(method=HttpMethod.GET, url=url)

    def get_user_by_task(self, task_id: int):
        url = f"{self.component_path}/client-by-task/{task_id}"
        self.response_model = UserResponse
        return self._construct_params(method=HttpMethod.GET, url=url)

    def get_user_proposed_tasks(self, user_id: int, proposed_by: PropositionBy):
        url = f"{self.component_path}/proposed-deals/{user_id}/{proposed_by}"
        self.response_model = TasksList
        return self._construct_params(method=HttpMethod.GET, url=url)
