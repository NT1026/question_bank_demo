from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from shutil import copyfileobj
from uuid import uuid4

from .depends import get_current_user
from api.response import (
    _302_REDIRECT_TO_HOME,
    _400_INVALID_ANSWER_FORMAT_API,
    _400_INVALID_FILE_TYPE_API,
    _403_NOT_A_TEACHER,
    _500_CREATE_QUESTION_FAILED_API,
)
from crud.question import QuestionCrudManager
from models.base import Role
from settings.configs import Settings

router = APIRouter()
templates = Jinja2Templates(directory="templates")
settings = Settings()

QuestionCrud = QuestionCrudManager()


@router.get(
    "/question/create",
    response_class=HTMLResponse,
)
async def question_create(
    request: Request,
    current_user=Depends(get_current_user),
):
    """
    新增題目頁面
    - 未登入使用者無法進入新增題目頁面，會被導向首頁
    - 已登入使用者，且使用者角色為非老師，無法進入新增題目頁面，會回應 403 錯誤
    - 已登入使用者，且使用者角色為老師，可進入新增題目頁面
    """
    # Check if user is teacher
    if not current_user:
        return _302_REDIRECT_TO_HOME

    if current_user.role != Role.TEACHER:
        return _403_NOT_A_TEACHER

    # Render question_create.html
    return templates.TemplateResponse(
        "question_create.html",
        {
            "request": request,
            "current_user": current_user,
        },
    )


@router.post(
    "/question/create",
    response_class=HTMLResponse,
)
async def question_create_post(
    request: Request,
    file: UploadFile = File(...),
    answer: str = Form(...),
    current_user=Depends(get_current_user),
):
    """
    新增題目頁面的 POST 請求處理
    - 未登入使用者無法進入新增題目頁面，會被導向首頁
    - 已登入使用者，且使用者角色為非老師，無法進入新增題目頁面，會回應 403 錯誤
    - 已登入使用者，且使用者角色為老師，可提交新增題目請求
    """
    # Check if user is teacher
    if not current_user:
        return _302_REDIRECT_TO_HOME

    if current_user.role != Role.TEACHER:
        return _403_NOT_A_TEACHER

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

    # Check if the question to be created already exists
    existing_question = await QuestionCrud.get_by_filename(f"{Path(file.filename).stem}")
    print(file.filename)
    if existing_question:
        return templates.TemplateResponse(
            "question_create.html",
            {
                "request": request,
                "current_user": current_user,
                "error": f"題目已存在：{file.filename}",
            },
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
        await QuestionCrud.create(
            id=question_id,
            subject=subject,
            image_path=str(image_path),
            answer=sorted_answer,
        )

        return templates.TemplateResponse(
            "question_create.html",
            {
                "request": request,
                "current_user": current_user,
                "success": f"已新增題目：{file.filename}",
            },
        )

    except Exception:
        raise _500_CREATE_QUESTION_FAILED_API


@router.get(
    "/question/read",
    response_class=HTMLResponse,
)
async def question_read(
    request: Request,
    current_user=Depends(get_current_user),
):
    """
    瀏覽題目頁面
    - 未登入使用者無法進入瀏覽題目頁面，會被導向首頁
    - 已登入使用者，且使用者角色為非老師，無法進入瀏覽題目頁面，會回應 403 錯誤
    - 已登入使用者，且使用者角色為老師，可進入瀏覽題目頁面
    """
    # Check if user is teacher
    if not current_user:
        return _302_REDIRECT_TO_HOME

    if current_user.role != Role.TEACHER:
        return _403_NOT_A_TEACHER

    # Render question_read.html
    return templates.TemplateResponse(
        "question_read.html",
        {
            "request": request,
            "current_user": current_user,
        },
    )


@router.get(
    "/question/delete",
    response_class=HTMLResponse,
)
async def question_delete(
    request: Request,
    current_user=Depends(get_current_user),
):
    """
    刪除題目頁面
    - 未登入使用者無法進入刪除題目頁面，會被導向首頁
    - 已登入使用者，且使用者角色為非老師，無法進入刪除題目頁面，會回應 403 錯誤
    - 已登入使用者，且使用者角色為老師，可進入刪除題目頁面
    """
    # Check if user is teacher
    if not current_user:
        return _302_REDIRECT_TO_HOME

    if current_user.role != Role.TEACHER:
        return _403_NOT_A_TEACHER

    # Render question_delete.html
    return templates.TemplateResponse(
        "question_delete.html",
        {
            "request": request,
            "current_user": current_user,
        },
    )


@router.post(
    "/question/delete",
    response_class=HTMLResponse,
)
async def question_delete_post(
    request: Request,
    filename: str = Form(...),
    current_user=Depends(get_current_user),
):
    """
    刪除題目頁面的 POST 請求處理
    - 未登入使用者無法進入刪除題目頁面，會被導向首頁
    - 已登入使用者，且使用者角色為非老師，無法進入刪除題目頁面，會回應 403 錯誤
    - 已登入使用者，且使用者角色為老師，可提交刪除題目請求
    """
    # Check if user is teacher
    if not current_user:
        return _302_REDIRECT_TO_HOME

    if current_user.role != Role.TEACHER:
        return _403_NOT_A_TEACHER

    # Check if the question(s) to be deleted exist(s)
    questions_to_delete = await QuestionCrud.get_by_filename(filename)
    if not questions_to_delete:
        return templates.TemplateResponse(
            "question_delete.html",
            {
                "request": request,
                "current_user": current_user,
                "error": f"找不到該題目：{filename}",
            },
        )

    # Delete all questions with the given filename
    await QuestionCrud.delete_by_filename(filename)
    return templates.TemplateResponse(
        "question_delete.html",
        {
            "request": request,
            "current_user": current_user,
            "success": f"已刪除指定題目：{filename}",
        },
    )
