from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class UserRole(str, Enum):
    student = "student"
    teacher = "teacher"


class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=10)
    name: str = Field(min_length=1, max_length=20)
    role: UserRole


class UserCreate(UserBase):
    password: str = Field(min_length=1, max_length=20)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "nt1026",
                    "name": "蔡承翰",
                    "role": "student",
                    "password": "password123",
                }
            ]
        }
    }


class UserRead(UserBase):
    id: str
    created_at: datetime
