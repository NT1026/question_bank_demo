from datetime import datetime
from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=1, max_length=10)
    password: str = Field(min_length=1, max_length=20)
    name: str = Field(min_length=1, max_length=10)
    role: str = Field(min_length=1, max_length=10)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "nt1026",
                    "password": "password",
                    "name": "蔡承翰",
                    "role": "student",
                }
            ]
        }
    }


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
