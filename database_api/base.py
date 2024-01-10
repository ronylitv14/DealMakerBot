from abc import ABC, abstractmethod
from typing import Optional, Union
from database_api.config import DB_API_TOKEN, DB_API_URL
from types import SimpleNamespace
from httpx import AsyncClient, Response
from pydantic import BaseModel, ConfigDict

from enum import StrEnum


class HttpMethod(StrEnum):
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'
    PATCH = 'PATCH'
    OPTIONS = 'OPTIONS'
    HEAD = 'HEAD'


class RequestParams(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    method: HttpMethod
    url: str
    data: Optional[dict] = None
    json: Optional[dict] = None
    headers: dict = {"token": DB_API_TOKEN}


class BaseAPI(ABC):
    def __init__(self, base_url: str = DB_API_URL):
        self.base_url = base_url
        self.headers = {"token": DB_API_TOKEN}
        self.params: Optional[RequestParams] = None
        self.response_model = None

    async def do_request(self):
        if self.params is None:
            raise AttributeError("You have to specify params using API requests!")
        async with AsyncClient() as client:
            request_params, response_model = self.params.model_dump(), self.response_model
            self.params, self.response_model = None, None
            resp = await client.request(**request_params)
            if resp.is_success and response_model is not None:
                if isinstance(resp.json(), list):
                    return response_model(list_values=resp.json())
                return response_model(**resp.json())
            return resp

    def construct_params(self, method: HttpMethod, url: str, json: Optional[dict] = None):
        self.params = RequestParams(method=method, url=url, json=json, headers=self.headers)
        return self
