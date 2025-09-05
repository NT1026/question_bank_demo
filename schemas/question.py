from datetime import datetime
from pydantic import BaseModel, Field


class QuestionRead(BaseModel):
    id: str
    subject: str = Field(min_length=1, max_length=20)
    image_path: str = Field(min_length=1, max_length=1000)
    answer: str = Field(min_length=1, max_length=4)
    created_at: datetime
