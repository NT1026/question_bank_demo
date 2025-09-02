from datetime import datetime
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import DeclarativeBase, mapped_column
from typing import Annotated


class Base(DeclarativeBase):
    pass


class BaseType:
    uuid = Annotated[str, mapped_column(String(36), primary_key=True)]

    hashed_password = Annotated[str, mapped_column(String(60))]
    int_type = Annotated[int, mapped_column(Integer)]
    str_10 = Annotated[str, mapped_column(String(10))]
    str_50 = Annotated[str, mapped_column(String(50))]
    datetime = Annotated[datetime, mapped_column(DateTime, nullable=True)]
    path = Annotated[str, mapped_column(String(1000), nullable=True)]
    json_type = Annotated[dict, mapped_column(JSON)]
