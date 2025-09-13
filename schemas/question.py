from pydantic import BaseModel, Field


class QuestionCreate(BaseModel):
    id: str = Field(min_length=1, max_length=36)
    subject: str = Field(min_length=1, max_length=20)
    image_path: str = Field(min_length=1, max_length=1000)
    answer: str = Field(min_length=1, max_length=4)
