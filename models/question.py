from datetime import datetime
from sqlalchemy.orm import Mapped, relationship
from uuid import uuid4

from models.base import Base, BaseType


class Question(Base):
    __tablename__ = "Question"
    id: Mapped[BaseType.uuid]
    subject: Mapped[BaseType.str_20]
    image_path: Mapped[BaseType.path]
    answer: Mapped[BaseType.str_10]
    created_at: Mapped[BaseType.datetime]

    def __init__(
        self,
        subject: str,
        image_path: str,
        answer: str,
    ):
        self.id = str(uuid4())
        self.subject = subject
        self.image_path = image_path
        self.answer = answer
        self.created_at = datetime.now()

    def __repr__(self):
        return f"Question(id={self.id}, subject={self.subject}, image_path={self.image_path}, answer={self.answer}, created_at={self.created_at})"
