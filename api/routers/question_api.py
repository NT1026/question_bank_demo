from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse
from itsdangerous import BadSignature, SignatureExpired
from pathlib import Path

from .depends import get_current_user
from api.response import (
    _403_INVALID_IMAGE_TOKEN_API,
    _403_IMAGE_TOKEN_EXPIRED_API,
    _403_NOT_LOGIN_API,
    _404_QUESTION_NOT_FOUND_API,
    _404_IMAGE_FILE_NOT_FOUND_API,
)
from auth.image import serializer
from crud.question import QuestionCrudManager
from settings.configs import Settings

router = APIRouter()
QuestionCrud = QuestionCrudManager()
settings = Settings()


@router.get("/image/{question_id}")
async def get_question_image(
    question_id: str,
    token: str = Query(...),
    current_user=Depends(get_current_user),
):
    # Check if not logged in
    if not current_user:
        raise _403_NOT_LOGIN_API

    # Validate token
    try:
        data = serializer.loads(token, max_age=10)
    except SignatureExpired:
        raise _403_IMAGE_TOKEN_EXPIRED_API
    except BadSignature:
        raise _403_INVALID_IMAGE_TOKEN_API

    # Check if token belongs to the current user
    if data["user_id"] != str(current_user.id):
        raise _403_INVALID_IMAGE_TOKEN_API

    # Check if question exists
    question = await QuestionCrud.get(question_id)
    if not question:
        raise _404_QUESTION_NOT_FOUND_API

    # Check if file (image_path) exists
    if not Path(question.image_path).exists():
        raise _404_IMAGE_FILE_NOT_FOUND_API

    return FileResponse(question.image_path, media_type="image/jpeg")
