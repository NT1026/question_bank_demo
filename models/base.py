from datetime import datetime
from enum import Enum
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import DeclarativeBase, mapped_column
from typing import Annotated


class Role(str, Enum):
    STUDENT = "student"
    TEACHER = "teacher"


class Base(DeclarativeBase):
    pass


class BaseType:
    uuid = Annotated[str, mapped_column(String(36), primary_key=True)]
    hashed_password = Annotated[str, mapped_column(String(60))]
    int_type = Annotated[int, mapped_column(Integer)]
    str_4 = Annotated[str, mapped_column(String(4))]
    str_10 = Annotated[str, mapped_column(String(10))]
    str_20 = Annotated[str, mapped_column(String(20))]
    str_30 = Annotated[str, mapped_column(String(30))]
    str_1000 = Annotated[str, mapped_column(String(1000))]
    datetime = Annotated[datetime, mapped_column(DateTime)]
    json_type = Annotated[dict, mapped_column(JSON)]
