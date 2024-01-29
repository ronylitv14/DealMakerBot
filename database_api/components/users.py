from typing import Optional, List

from database_api.base import BaseAPI, HttpMethod, APIListObject
from pydantic import BaseModel, ConfigDict
from utils.hashing_passwords import check_user_password
import enum


class UserStatus(enum.StrEnum):
    default: str = "default_user"
    admin: str = "admin"
    superuser: str = "superuser"


class UserType(enum.StrEnum):
    client: str = "client"
    executor: str = "executor"


class UserResponse(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    telegram_id: int
    telegram_username: str
    username: str
    chat_id: int
    user_status: UserStatus
    is_banned: bool
    warning_count: int
    salt: str
    hashed_password: str
    phone: Optional[str] = None
    email: Optional[str] = None

    def check_password(self, password: str):
        return check_user_password(
            password_attempt=password,
            stored_hash=self.hashed_password,
            stored_salt=self.salt
        )

    def __str__(self):
        return f"Ім'я користувача: {self.username}, Статус користувача: {self.user_status}"


class UserResponseList(APIListObject):
    list_values: List[UserResponse]


class Users(BaseAPI):
    def __init__(self):
        super().__init__()
        self.component_path = f"{self.base_url}/users"

    def get_user_from_db(self, telegram_id: int):
        url = f"{self.component_path}/{telegram_id}"
        self.response_model = UserResponse
        return self._construct_params(method=HttpMethod.GET, url=url)

    def delete_user_from_db(self, telegram_id: int):
        url = f"{self.component_path}/{telegram_id}"
        return self._construct_params(method=HttpMethod.DELETE, url=url)

    def update_user(self, telegram_id: int, user_email: Optional[str] = None, nickname: Optional[str] = None,
                    phone: Optional[str] = None):
        url = f"{self.component_path}/{telegram_id}"
        json = {
            "email": user_email,
            "nickname": nickname,
            "phone": phone
        }
        return self._construct_params(method=HttpMethod.PATCH, url=url, json=json)

    def create_user(self, telegram_id: int, username: str, password: str, tg_username: str, chat_id: int,
                    user_email: Optional[str] = None, phone: Optional[str] = None):
        url = f"{self.component_path}/"
        json = {
            "telegram_id": telegram_id,
            "username": username,
            "phone": phone,
            "password": password,
            "chat_id": chat_id,
            "tg_username": tg_username,
            "email": user_email
        }
        return self._construct_params(method=HttpMethod.POST, url=url, json=json)

    def get_all_users_except_admins(self):
        url = f"{self.component_path}/default-users/"
        self.response_model = UserResponseList
        return self._construct_params(method=HttpMethod.GET, url=url)

    def ban_user(self, user_id: int, is_banned: bool):
        url = f"{self.component_path}/ban/"
        json = {
            "user_id": user_id,
            "is_banned": is_banned
        }
        return self._construct_params(method=HttpMethod.PATCH, url=url, json=json)

    def get_similar_users(self, name: str, is_executor: bool = False):
        url = f"{self.component_path}/similarity/{name}/{is_executor}"
        self.response_model = UserResponseList
        return self._construct_params(method=HttpMethod.GET, url=url)
