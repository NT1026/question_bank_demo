from datetime import datetime
from enum import Enum
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import DeclarativeBase, mapped_column
from typing import Annotated


class Role(str, Enum):
    ADMIN = "admin"
    STUDENT = "student"
    TEACHER = "teacher"


class Subject(str, Enum):
    MATH = "math"
    NATURE_SCIENCE = "nature_science"


class Exam_type(str, Enum):
    MATH_ACHIEVEMENT = "math_achievement"
    MATH_APTITUDE = "math_aptitude"
    NATURE_SCIENCE_ACHIEVEMENT = "nature_science_achievement"
    NATURE_SCIENCE_APTITUDE = "nature_science_aptitude"


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
