import os

import aiohttp
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

X_TOKEN = os.getenv('X_TOKEN')


class HeaderInfo:
    def __init__(self, x_token: str, x_cms: Optional[str] = None, x_cms_version: Optional[str] = None):
        self.x_token = {"X-Token": x_token}
        self.x_cms = {"X-CMS": x_cms} if x_cms else None
        self.x_cms_version = {"X-CMS-Version": x_cms_version} if x_cms_version else None

    def to_dict(self):
        headers_data = {}
        for key, val in self.__dict__.items():
            if val:
                headers_data.update(val)

        return headers_data


class BodyInfo:
    def __init__(self, amount: int, webhook_url: str, redirect_url: Optional[str] = None, ccy: int = 980,
                 validity: Optional[int] = None,
                 payment_type: str = "debit"):
        self.amount = amount
        self.ccy = ccy
        self.redirectUrl = redirect_url
        self.webHookUrl = webhook_url
        self.validity = validity
        self.paymentType = payment_type

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if v is not None}


async def get_invoice_payment_link(header_info: HeaderInfo, body_info: BodyInfo):
    url = 'https://api.monobank.ua/api/merchant/invoice/create'
    headers = header_info.to_dict()
    body = body_info.to_dict()

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=body) as response:
            if response.status not in [200, 201]:
                print("Error")
                raise ValueError("Error with creating invoice!")
            return await response.json()
