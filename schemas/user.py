from datetime import datetime
from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str
    name: str
    role: str


class UserRead(BaseModel):
    id: str
    username: str
    name: str
    role: str
    created_at: datetime


class UserUpdate(BaseModel):
    name: str


class UserUpdatePassword(BaseModel):
    password: str
