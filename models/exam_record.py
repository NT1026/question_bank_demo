from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import uuid4

from models.base import Base, BaseType
from schemas.exam_record import UserAnswer


class ExamRecord(Base):
    __tablename__ = "ExamRecord"
    id: Mapped[BaseType.uuid]
    user_id: Mapped[BaseType.uuid] = mapped_column(
        ForeignKey("User.id", ondelete="CASCADE")
    )
    subject: Mapped[BaseType.str_20]
    score: Mapped[BaseType.int_type]
    user_answers: Mapped[BaseType.json_type]
    created_at: Mapped[BaseType.datetime]

    # relationship to parent
    user_info: Mapped["User"] = relationship(
        "User",
        back_populates="exam_records",
        lazy="joined",
    )

    def __init__(
        self,
        user_id: str,
        subject: str,
        score: int,
        user_answers: list[UserAnswer],
        id=str(uuid4()),
        created_at: datetime = datetime.now(),
    ):
        self.id = id
        self.user_id = user_id
        self.subject = subject
        self.score = score
        self.user_answers = (
            [item.model_dump() for item in user_answers] if user_answers else []
        )
        self.created_at = created_at

    def __repr__(self):
        return f"ExamRecord(id={self.id}, user_id={self.user_id}, subject={self.subject}, score={self.score}, user_answers={self.user_answers}, created_at={self.created_at})"
