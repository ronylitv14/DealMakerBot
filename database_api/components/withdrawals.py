import datetime
import decimal
from typing import Optional, List
from pydantic import BaseModel, condecimal, ConfigDict
from database_api.base import BaseAPI, HttpMethod, APIListObject

import enum


class WithdrawalStatus(enum.StrEnum):
    pending: str = "pending"
    processed: str = "processed"
    rejected: str = "rejected"


class WithdrawalRequestModel(BaseModel):
    model_config = ConfigDict(use_enum_values=True, from_attributes=True)
    request_id: int
    user_id: int
    amount: float
    commission: float
    request_date: datetime.datetime = datetime.datetime.now
    status: WithdrawalStatus
    payment_method: str
    payment_details: Optional[str] = None
    processed_date: Optional[datetime.datetime] = None
    admin_id: Optional[int] = None
    notes: Optional[str] = None

    def __str__(self):
        return f"Номер заявки: {self.request_id}, Заявка на виплату: {self.amount} + {self.commission}"


class WithdrawalRequestList(APIListObject):
    list_values: List[WithdrawalRequestModel]


class Withdrawals(BaseAPI):
    def __init__(self):
        super().__init__()
        self.component_path = f"{self.base_url}/withdrawals"

    def save_withdrawal_data(self, user_id: int, amount: decimal.Decimal, commission: decimal.Decimal,
                             status: WithdrawalStatus, payment_method: str):
        url = f"{self.component_path}/"

        json = {
            "user_id": user_id,
            "amount": float(amount),
            "commission": float(commission),
            "status": status,
            "payment_method": payment_method
        }
        return self._construct_params(method=HttpMethod.POST, url=url, json=json)

    def get_withdrawals_data(self, status: WithdrawalStatus = WithdrawalStatus.pending):
        url = f"{self.component_path}/{status}"
        self.response_model = WithdrawalRequestList
        return self._construct_params(method=HttpMethod.GET, url=url)

    def update_withdrawal_request(self, request_id: int, new_status: WithdrawalStatus, admin_id: int):
        url = f"{self.component_path}/"

        json = {
            "request_id": request_id,
            "new_status": new_status,
            "admin_id": admin_id,
            # "processed_time": processed_date
        }
        return self._construct_params(method=HttpMethod.PATCH, json=json, url=url)
