from datetime import datetime
from pydantic import BaseModel, Field


class QuestionBase(BaseModel):
    subject: str = Field(min_length=1, max_length=20)
    image_path: str = Field(min_length=1, max_length=1000)
    answer: str = Field(min_length=1, max_length=10)


class QuestionCreate(QuestionBase):
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "subject": "math",
                    "image_path": "/questions/math001.png",
                    "answer": "1",
                }
            ]
        }
    }


class QuestionRead(QuestionBase):
    id: str
    created_at: datetime
