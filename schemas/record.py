from datetime import datetime
from pydantic import BaseModel, Field


class UserAnswerCreate(BaseModel):
    question_id: str
    user_answer: str
    answer: str


class RecordCreate(BaseModel):
    subject: str = Field(min_length=1, max_length=10)
    user_answers: list[UserAnswerCreate]

    model_config = {
        "json_schema_extra": {
            "examples": [
                { 
                    "subject": "math",
                    "user_answers": [
                        {
                            "question_id": "question-uuid-1",
                            "user_answer": "1",
                            "answer": "1"
                        },
                        {
                            "question_id": "question-uuid-2",
                            "user_answer": "1",
                            "answer": "2"
                        }
                    ]
                }
            ]
        }
    }


class RecordRead(BaseModel):
    id: str
    user_id: str
    subject: str
    score: int
    user_answers: list[UserAnswerCreate]
    created_at: datetime
