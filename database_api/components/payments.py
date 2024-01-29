import decimal
from database_api.base import BaseAPI, HttpMethod
from pydantic import BaseModel
from database_api.components.transactions import TransactionModel


class SuccessModel(BaseModel):
    status: bool


class Payments(BaseAPI):
    def __init__(self):
        super().__init__()
        self.component_path = f"{self.base_url}/payments"

    def perform_money_transfer(self, receiver_id: int, sender_id: int, task_id: int, amount: decimal.Decimal):
        url = f"{self.component_path}/transfer"

        json = {
            "receiver_id": receiver_id,
            "sender_id": sender_id,
            "task_id": task_id,
            "amount": float(amount)
        }
        self.response_model = TransactionModel
        return self._construct_params(method=HttpMethod.POST, url=url, json=json)

    def check_payment_status(self, task_id: int, receiver_id: int, sender_id: int):
        url = f"{self.component_path}/{task_id}/{receiver_id}/{sender_id}"
        self.response_model = SuccessModel
        return self._construct_params(method=HttpMethod.GET, url=url)

    def accept_offer(self, transaction_id: int, task_id: int, receiver_id: int, amount: decimal.Decimal = None):
        url = f"{self.component_path}/accept-offer"
        json = {
            "transaction_id": transaction_id,
            "task_id": task_id,
            "receiver_id": receiver_id,
            # "amount": float(amount)
        }
        return self._construct_params(method=HttpMethod.POST, url=url, json=json)
