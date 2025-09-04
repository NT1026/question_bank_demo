from datetime import datetime
from pydantic import BaseModel, Field


class UserAnswer(BaseModel):
    question_id: str
    user_answer: str


class ExamRecordBase(BaseModel):
    subject: str = Field(min_length=1, max_length=20)


class ExamRecordCreate(ExamRecordBase):
    user_answers: list[UserAnswer]

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
    user_answers: list[UserAnswer]
    created_at: datetime
