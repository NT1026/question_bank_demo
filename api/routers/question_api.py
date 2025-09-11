from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse
from itsdangerous import BadSignature, SignatureExpired
from pathlib import Path

from .depends import get_current_user
from api.response import (
    _403_INVALID_IMAGE_TOKEN_API,
    _403_IMAGE_TOKEN_EXPIRED_API,
    _404_IMAGE_FILE_NOT_FOUND_API,
)
from auth.image import serializer
from crud.question import QuestionCrudManager
from settings.configs import Settings

router = APIRouter()
QuestionCrud = QuestionCrudManager()
settings = Settings()


@router.get("/image/{question_id}", response_class=FileResponse)
async def get_question_image(
    question_id: str,
    token: str = Query(...),
    current_user=Depends(get_current_user),
):
    try:
        data = serializer.loads(token, max_age=10)
    except SignatureExpired:
        raise _403_IMAGE_TOKEN_EXPIRED_API
    except BadSignature:
        raise _403_INVALID_IMAGE_TOKEN_API

    # Check if token belongs to the current user
    if data["user_id"] != str(current_user.id):
        raise _403_INVALID_IMAGE_TOKEN_API

    # Check if file (image_path) exists
    question = await QuestionCrud.get(question_id)
    if not question or not Path(question.image_path).exists():
        raise _404_IMAGE_FILE_NOT_FOUND_API

    return FileResponse(question.image_path, media_type="image/jpeg")
