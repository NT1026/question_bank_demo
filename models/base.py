from datetime import datetime
from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import DeclarativeBase, mapped_column
from typing import Annotated, Optional


class Base(DeclarativeBase):
    pass


class BaseType:
    uuid = Annotated[str, mapped_column(String(36), primary_key=True)]

    hashed_password = Annotated[str, mapped_column(String(60))]
    boolean = Annotated[bool, mapped_column(Boolean)]
    int_type = Annotated[int, mapped_column(Integer)]
    str_10 = Annotated[str, mapped_column(String(10))]
    str_50 = Annotated[str, mapped_column(String(50))]
    optional_str_200 = Annotated[
        Optional[str], mapped_column(String(200), nullable=True)
    ]
    datetime = Annotated[datetime, mapped_column(DateTime, nullable=True)]
    path = Annotated[str, mapped_column(String(1000), nullable=True)]
    json_type = Annotated[dict, mapped_column(JSON)]
