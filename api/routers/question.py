from fastapi import APIRouter, Depends, File, Form, Query, status, UploadFile
from fastapi.responses import FileResponse
from itsdangerous import BadSignature, SignatureExpired
from pathlib import Path
from shutil import copyfileobj
from uuid import uuid4

from .depends import get_current_user
from api.response import (
    _400_INVALID_ANSWER_FORMAT_API,
    _400_INVALID_FILE_TYPE_API,
    _403_INVALID_IMAGE_TOKEN_API,
    _403_IMAGE_TOKEN_EXPIRED_API,
    _404_IMAGE_FILE_NOT_FOUND_API,
    _500_CREATE_QUESTION_FAILED_API,
)
from auth.image import serializer
from crud.question import QuestionCrudManager
from schemas import question as QuestionSchema
from settings.configs import Settings


router = APIRouter()
QuestionCrud = QuestionCrudManager()
settings = Settings()


@router.post(
    "",
    response_model=QuestionSchema.QuestionRead,
    status_code=status.HTTP_201_CREATED,
    deprecated=True,
)
async def create_question(
    file: UploadFile = File(...),
    answer: str = Form(...),
):
    """
    用以下資訊建立新題目：
    - 上傳一張 JPG 圖片
    - answer
    """
    # Check answer format is valid
    sorted_answer = "".join(sorted(list(item for item in answer.upper())))
    if (
        not sorted_answer
        or not all(c in "ABCD" for c in sorted_answer)
        or len(sorted_answer) > 4
    ):
        raise _400_INVALID_ANSWER_FORMAT_API

    # File type check
    if file.content_type not in ["image/jpeg"]:
        raise _400_INVALID_FILE_TYPE_API

    # Write file to disk
    try:
        is_math = file.filename.startswith("M")
        subject = "math" if is_math else "nature_science"
        subject_folder = (
            settings.MATH_DIRNAME if is_math else settings.NATURE_SCIENCE_DIRNAME
        )
        question_id = str(uuid4())

        base_path = Path(settings.PROTECTED_IMG_DIR)
        base_path.mkdir(parents=True, exist_ok=True)
        (base_path / subject_folder).mkdir(parents=True, exist_ok=True)

        image_path = (
            base_path / subject_folder / f"{Path(file.filename).stem}_{question_id}.jpg"
        )
        with image_path.open("wb") as f:
            copyfileobj(file.file, f)

        # Write into database
        question = await QuestionCrud.create(
            id=question_id,
            subject=subject,
            image_path=str(image_path),
            answer=sorted_answer,
        )

        return question

    except Exception:
        raise _500_CREATE_QUESTION_FAILED_API


@router.get(
    "/image/{question_id}",
    response_class=FileResponse,
)
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
