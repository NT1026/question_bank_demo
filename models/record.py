from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, BaseType
from schemas.record import UserAnswerCreate


class Record(Base):
    __tablename__ = "Record"
    id: Mapped[BaseType.uuid]
    user_id: Mapped[BaseType.uuid] = mapped_column(
        ForeignKey("User.id", ondelete="CASCADE")
    )
    subject: Mapped[BaseType.str_10]
    score: Mapped[BaseType.int_type]
    user_answers: Mapped[BaseType.json_type]
    created_at: Mapped[BaseType.datetime]

    # relationships to parent
    user_info: Mapped["User"] = relationship(
        "User",
        back_populates="exam_records",
        lazy="joined",
    )

    def __init__(
        self,
        id: str,
        user_id: str,
        subject: str,
        score: int,
        user_answers: list[UserAnswerCreate],
        created_at: datetime,
    ):
        self.id = id
        self.user_id = user_id
        self.subject = subject
        self.score = score
        self.user_answers = [item.model_dump() for item in user_answers]
        self.created_at = created_at

    def __repr__(self):
        return f"Exam(id={self.id}, user_id={self.user_id}, subject={self.subject}, score={self.score}, user_answers={self.user_answers}, created_at={self.created_at})"
