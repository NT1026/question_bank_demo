from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    status,
    UploadFile,
)
from fastapi.responses import FileResponse
from itsdangerous import BadSignature, SignatureExpired
from pathlib import Path
from shutil import copyfileobj
from uuid import uuid4

from .depends import check_question_id, get_current_user
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
    answer = answer.upper()
    if not answer or not all(c in "ABCD" for c in answer) or len(answer) > 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Answer must be combination of A/B/C/D, 1~4 characters",
        )

    # File type check
    if file.content_type not in ["image/jpeg"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a JPG image",
        )

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
            answer=answer,
        )

        return question

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {e}",
        )


@router.get(
    "/subject/{subject}",
    response_model=list[QuestionSchema.QuestionRead],
    status_code=status.HTTP_200_OK,
)
async def read_questions_by_subject(subject: str):
    """
    根據科目取得該科目所有題目
    """
    questions = await QuestionCrud.get_by_subject(subject)
    return questions


@router.delete(
    "/{question_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_question(question_id: str = Depends(check_question_id)):
    """
    根據 question_id 刪除題目
    """
    await QuestionCrud.delete(question_id)
    return


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
        # Only valid for 5 minutes
        data = serializer.loads(token, max_age=10)
    except SignatureExpired:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token expired",
        )
    except BadSignature:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token",
        )

    # Check if token belongs to the current user
    if data["user_id"] != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )

    # Check if filename matches
    question = await QuestionCrud.get(question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found",
        )

    return FileResponse(question.image_path, media_type="image/jpeg")
