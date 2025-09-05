from datetime import datetime
from sqlalchemy.orm import Mapped, relationship
from uuid import uuid4

from models.base import Base, BaseType


class User(Base):
    __tablename__ = "User"
    id: Mapped[BaseType.uuid]
    username: Mapped[BaseType.str_10]
    password: Mapped[BaseType.hashed_password]
    name: Mapped[BaseType.str_20]
    role: Mapped[BaseType.str_10]
    created_at: Mapped[BaseType.datetime]

    # relationship to child
    exam_records: Mapped[list["ExamRecord"]] = relationship(
        "ExamRecord",
        back_populates="user_info",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __init__(
        self,
        username: str,
        password: str,
        name: str,
        role: str,
        id: str = str(uuid4()),
        created_at: datetime = datetime.now(),
    ):
        self.id = id
        self.username = username
        self.password = password
        self.name = name
        self.role = role
        self.created_at = created_at

    def __repr__(self):
        return f"User(id={self.id}, username={self.username}, password={self.password}, name={self.name}, role={self.role}, created_at={self.created_at})"
