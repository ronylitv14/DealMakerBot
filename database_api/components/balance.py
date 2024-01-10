import decimal
from typing import List, Optional

from database_api.base import BaseAPI, HttpMethod
from pydantic import BaseModel, condecimal
import enum


class BalanceAction(enum.StrEnum):
    replenishment: str = "replenishment"
    withdrawal: str = "withdrawal"


class BalanceModel(BaseModel):
    user_id: int
    user_cards: Optional[List]
    balance_money: condecimal(max_digits=10, decimal_places=2)


class Balance(BaseAPI):
    def __init__(self):
        super().__init__()
        self.component_path = f"{self.base_url}/balance"

    def get_user_balance(self, user_id: int):
        url = f"{self.component_path}/{user_id}"
        self.response_model = BalanceModel
        return self.construct_params(method=HttpMethod.GET, url=url)

    def post_user_balance(self, user_id: int):
        url = f"{self.component_path}/{user_id}"
        return self.construct_params(method=HttpMethod.POST, url=url)

    def update_user_cards(self, user_id: int, card: str):
        url = f"{self.component_path}/user-cards/"
        json = {
            "user_id": user_id,
            "card": card
        }
        return self.construct_params(method=HttpMethod.PATCH, url=url, json=json)

    def reset_user_balance(self, user_id: int, new_amount: decimal.Decimal):
        url = f"{self.component_path}/new/"
        json = {
            "user_id": user_id,
            "new_amount": float(new_amount)
        }
        return self.construct_params(method=HttpMethod.PATCH, url=url, json=json)

    def perform_fund_transfer(self, user_id: int, amount: decimal.Decimal, action: BalanceAction):
        url = f"{self.component_path}/fund-transfer/"

        json = {
            "user_id": user_id,
            "amount": float(amount),
            "action": action
        }
        return self.construct_params(method=HttpMethod.PATCH, url=url, json=json)
