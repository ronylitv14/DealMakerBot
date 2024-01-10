import datetime
import decimal
from typing import Optional, List
from database_api.base import BaseAPI, HttpMethod
from pydantic import BaseModel, condecimal, ConfigDict
import enum


class TransactionType(enum.StrEnum):
    debit: str = 'Debit'
    transfer: str = 'Transfer'
    withdrawal: str = "Withdrawal"


class TransactionStatus(enum.StrEnum):
    pending: str = 'Pending'
    completed: str = 'Completed'
    failed: str = 'Failed'


class TransactionModel(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    transaction_id: int
    invoice_id: str
    sender_id: Optional[int] = None
    receiver_id: Optional[int] = None
    task_id: Optional[int] = None
    amount: condecimal(max_digits=10, decimal_places=2)
    commission: Optional[condecimal(max_digits=10, decimal_places=2)] = 0.00
    transaction_type: TransactionType
    transaction_status: TransactionStatus
    transaction_date: Optional[datetime] = None


class TransactionList(BaseModel):
    list_values: List[TransactionModel]


class Transactions(BaseAPI):
    def __init__(self):
        super().__init__()
        self.component_path = f"{self.base_url}/transactions"

    def save_transaction_data(self, invoice_id: str,
                              amount: decimal.Decimal,
                              transaction_type: TransactionType,
                              transaction_status: TransactionStatus,
                              sender_id: Optional[int] = None,
                              receiver_id: Optional[int] = None,
                              task_id: Optional[int] = None):
        url = f"{self.component_path}/"

        json = {
            "invoice_id": invoice_id,
            "amount": amount,
            "transaction_type": transaction_type,
            "transaction_status": transaction_status,
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "task_id": task_id
        }
        return self.construct_params(method=HttpMethod.POST, url=url, json=json)

    def update_transaction_status(self, invoice_id: str, new_status: TransactionStatus):
        url = f"{self.component_path}/"
        json = {
            "invoice_id": invoice_id,
            "new_status": new_status
        }
        return self.construct_params(method=HttpMethod.PATCH, url=url, json=json)

    def get_user_transactions(self, user_id: int):
        url = f"{self.component_path}/{user_id}"
        self.response_model = TransactionList
        return self.construct_params(method=HttpMethod.GET, url=url)
