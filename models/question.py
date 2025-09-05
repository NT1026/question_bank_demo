from datetime import datetime
from sqlalchemy.orm import Mapped, relationship
from uuid import uuid4

from models.base import Base, BaseType


class Question(Base):
    __tablename__ = "Question"
    id: Mapped[BaseType.uuid]
    subject: Mapped[BaseType.str_20]
    image_path: Mapped[BaseType.str_1000]
    answer: Mapped[BaseType.str_4]
    created_at: Mapped[BaseType.datetime]

    def __init__(
        self,
        subject: str,
        image_path: str,
        answer: str,
        id: str = str(uuid4()),
        created_at: datetime = datetime.now(),
    ):
        self.id = id
        self.subject = subject
        self.image_path = image_path
        self.answer = answer
        self.created_at = created_at

    def __repr__(self):
        return f"Question(id={self.id}, subject={self.subject}, image_path={self.image_path}, answer={self.answer}, created_at={self.created_at})"
