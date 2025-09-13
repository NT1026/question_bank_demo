from pydantic import BaseModel, Field


class UserAnswer(BaseModel):
    question_id: str
    user_answer: str


class ExamRecordCreate(BaseModel):
    exam_type: str = Field(min_length=1, max_length=30)
    user_answers: list[UserAnswer]
