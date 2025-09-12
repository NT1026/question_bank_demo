from csv import DictReader
from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from io import StringIO

from .depends import get_current_user
from api.response import (
    _302_REDIRECT_TO_HOME,
    _403_NOT_A_TEACHER,
)
from crud.question import QuestionCrudManager
from models.base import Role
from settings.configs import Settings

router = APIRouter()
templates = Jinja2Templates(directory="templates")
settings = Settings()

QuestionCrud = QuestionCrudManager()


@router.get("", response_class=HTMLResponse)
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


@router.post("", response_class=HTMLResponse)
async def single_question_delete_post(
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
                "error_single": f"找不到該題目：{filename}",
            },
        )

    # Delete all questions with the given filename
    await QuestionCrud.delete_by_filename(filename)
    return templates.TemplateResponse(
        "question_delete.html",
        {
            "request": request,
            "current_user": current_user,
            "success_single": f"已刪除指定題目：{filename}",
        },
    )


@router.post("/bulk", response_class=HTMLResponse)
async def multiple_question_delete_post(
    request: Request,
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
):
    """
    批次刪除題目頁面的 POST 請求處理
    - 未登入使用者無法進入刪除題目頁面，會被導向首頁
    - 已登入使用者，且使用者角色為非老師，無法進入刪除題目頁面，會回應 403 錯誤
    - 已登入使用者，且使用者角色為老師，可提交批次刪除題目請求
    """
    # Check if user is teacher
    if not current_user:
        return _302_REDIRECT_TO_HOME

    if current_user.role != Role.TEACHER:
        return _403_NOT_A_TEACHER

    # Read CSV file
    content = await file.read()
    decoded_content = content.decode("utf-8")
    csv_reader = DictReader(StringIO(decoded_content))

    success_questions = []
    error_questions = []

    for row in csv_reader:
        serial_number = row.get("serial_number").strip()
        question_to_delete = await QuestionCrud.get_by_filename(serial_number)
        if question_to_delete:
            await QuestionCrud.delete_by_filename(serial_number)
            success_questions.append(serial_number)

        else:
            error_questions.append(serial_number)

    success_message = (
        f"已刪除題目：{', '.join(success_questions)}" if success_questions else ""
    )

    error_message = (
        f"找不到以下題目：{', '.join(error_questions)}" if error_questions else ""
    )

    return templates.TemplateResponse(
        "question_delete.html",
        {
            "request": request,
            "current_user": current_user,
            "success_multiple": success_message,
            "error_multiple": error_message,
        },
    )
