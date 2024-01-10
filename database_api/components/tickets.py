import datetime
from typing import Optional, List
from urllib.parse import urlencode
from pydantic import BaseModel, ConfigDict
from database_api.base import BaseAPI, HttpMethod, RequestParams

import enum


class TicketStatus(enum.StrEnum):
    open = "Open"
    in_progress = "In Progress"
    closed = "Closed"


class UserTicketModel(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    ticket_id: int
    user_id: int
    subject: str
    description: str
    status: TicketStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    response: Optional[str] = None
    responded_by: Optional[int] = None


class TicketsList(BaseModel):
    list_values: List[UserTicketModel]


class Tickets(BaseAPI):
    def __init__(self):
        super().__init__()
        self.component_path = f"{self.base_url}/tickets"

    def save_ticket_data(self, user_id: int, description: str, subject: str):
        url = f"{self.component_path}/"

        json = {
            "user_id": user_id,
            "description": description,
            "subject": subject
        }
        return self.construct_params(method=HttpMethod.POST, url=url, json=json)

    def get_ticket_json(self, ticket_status: TicketStatus):
        url = f"{self.component_path}/"
        url = url + "?" + urlencode(dict(ticket_status=ticket_status))
        self.response_model = TicketsList
        return self.construct_params(method=HttpMethod.GET, url=url)

    def update_ticket_status(self, ticket_id: int, new_status: TicketStatus, admin_id: int):
        url = f"{self.component_path}/{ticket_id}"
        json = {
            "new_status": new_status,
            "admin_id": admin_id
        }
        return self.construct_params(method=HttpMethod.PATCH, url=url, json=json)
