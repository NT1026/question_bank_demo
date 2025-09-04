from datetime import datetime
from pydantic import BaseModel, Field


class UserAnswer(BaseModel):
    question_id: str
    user_answer: str


class ExamRecordBase(BaseModel):
    subject: str = Field(min_length=1, max_length=20)
    user_answers: list[UserAnswer]


class ExamRecordCreate(ExamRecordBase):
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "subject": "math",
                    "user_answers": [
                        {
                            "question_id": "question-uuid-1",
                            "user_answer": "1",
                        },
                        {
                            "question_id": "question-uuid-2",
                            "user_answer": "1",
                        },
                    ],
                }
            ]
        }
    }


class ExamRecordRead(ExamRecordBase):
    id: str
    user_id: str
    score: int
    created_at: datetime
