from enum import Enum
from pydantic import BaseModel, Field


class UserRole(str, Enum):
    student = "student"
    teacher = "teacher"


class UserCreate(BaseModel):
    username: str = Field(min_length=1, max_length=10)
    password: str = Field(min_length=1, max_length=20)
    name: str = Field(min_length=1, max_length=20)
    role: UserRole
