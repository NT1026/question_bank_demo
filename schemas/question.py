from datetime import datetime
from pydantic import BaseModel


class QuestionCreate(BaseModel):
    subject: str
    image_path: str
    answer: str


class QuestionRead(BaseModel):
    id: str
    subject: str
    image_path: str
    answer: str
    created_at: datetime
