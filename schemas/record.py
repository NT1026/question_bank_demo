from datetime import datetime
from pydantic import BaseModel


class UserAnswerCreate(BaseModel):
    question_id: str
    user_answer: str
    answer: str


class RecordCreate(BaseModel):
    subject: str
    user_answers: list[UserAnswerCreate]


class RecordRead(BaseModel):
    id: str
    user_id: str
    subject: str
    score: int
    user_answers: list[UserAnswerCreate]
    created_at: datetime
