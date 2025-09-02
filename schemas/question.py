from datetime import datetime
from pydantic import BaseModel, Field


class QuestionCreate(BaseModel):
    subject: str = Field(min_length=1, max_length=10)
    image_path: str = Field(min_length=1, max_length=1000)
    answer: str = Field(min_length=1, max_length=10)

    model_config = {
        "json_schema_extra": {
            "examples": [
                { 
                    "subject": "math",
                    "image_path": "/static/questions/math001.png",
                    "answer": "1"
                }
            ]
        }
    }


class QuestionRead(BaseModel):
    id: str
    subject: str
    image_path: str
    answer: str
    created_at: datetime
