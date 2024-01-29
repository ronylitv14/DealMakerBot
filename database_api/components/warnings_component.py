from pydantic import BaseModel
from database_api.base import BaseAPI, HttpMethod

from datetime import datetime
from typing import Optional


class WarningModel(BaseModel):
    warning_id: int
    user_id: int
    reason: str
    issued_by: int
    issued_at: Optional[datetime] = None

    def __str__(self):
        return f"Попередження: {self.reason}"


class Warnings(BaseAPI):
    def __init__(self):
        super().__init__()
        self.component_path = f"{self.base_url}/warnings"

    def save_warning_data(
            self,
            user_id: int,
            reason: str,
            issued_by: int,
            warning_count: int
    ):
        url = f"{self.component_path}/"

        json = {
            "user_id": user_id,
            "reason": reason,
            "issued_by": issued_by,
            "warning_count": warning_count
        }
        return self._construct_params(method=HttpMethod.POST, url=url, json=json)
