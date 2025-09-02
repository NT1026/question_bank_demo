from datetime import datetime
from sqlalchemy.orm import Mapped

from models.base import Base, BaseType


class Question(Base):
    __tablename__ = "Question"
    id: Mapped[BaseType.uuid]
    subject: Mapped[BaseType.str_10]
    image_path: Mapped[BaseType.path]
    answer: Mapped[BaseType.str_10]
    created_at: Mapped[BaseType.datetime]

    def __init__(
        self,
        id: str,
        subject: str,
        image_path: str,
        answer: str,
        created_at: datetime,
    ):
        self.id = id
        self.subject = subject
        self.image_path = image_path
        self.answer = answer
        self.created_at = created_at

    def __repr__(self):
        return f"Question(id={self.id}, subject={self.subject}, image_path={self.image_path}, answer={self.answer}, created_at={self.created_at})"
