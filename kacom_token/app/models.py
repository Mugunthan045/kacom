from datetime import datetime
from typing import Union

from pydantic import BaseModel


class User(BaseModel):
    username: str
    email: Union[str, None] = None

    class Config:
        allow_population_by_field_name = True


class UserInDB(User):
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None
