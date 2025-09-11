from csv import writer
from datetime import datetime
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from io import StringIO
from pathlib import Path

from .depends import get_current_user
from api.response import (
    _302_REDIRECT_TO_HOME,
    _403_NOT_A_TEACHER,
)
from auth.image import generate_image_token
from crud.question import QuestionCrudManager
from models.base import Role, Subject
from settings.configs import Settings

router = APIRouter()
templates = Jinja2Templates(directory="templates")
settings = Settings()

QuestionCrud = QuestionCrudManager()


@router.get("", response_class=HTMLResponse)
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


@router.post("", response_class=HTMLResponse)
async def single_question_read_post(
    request: Request,
    filename: str = Form(...),
    current_user=Depends(get_current_user),
):
    """
    瀏覽題目頁面的 POST 請求處理
    - 未登入使用者無法進入瀏覽題目頁面，會被導向首頁
    - 已登入使用者，且使用者角色為非老師，無法進入瀏覽題目頁面，會回應 403 錯誤
    - 已登入使用者，且使用者角色為老師，可提交瀏覽題目請求
    """
    # Check if user is teacher
    if not current_user:
        return _302_REDIRECT_TO_HOME

    if current_user.role != Role.TEACHER:
        return _403_NOT_A_TEACHER

    # Check if the question to be viewed exists
    question = await QuestionCrud.get_by_filename(filename)
    if not question:
        return templates.TemplateResponse(
            "question_read.html",
            {
                "request": request,
                "current_user": current_user,
                "error_single": f"找不到該題目：{filename}",
            },
        )

    # Get image token and render question_read.html
    question.image_name = str(Path(question.image_path).name)[:6] + ".jpg"
    question.token = generate_image_token(str(current_user.id), question.id)
    return templates.TemplateResponse(
        "question_read.html",
        {
            "request": request,
            "current_user": current_user,
            "question": question,
        },
    )


@router.post("/bulk", response_class=HTMLResponse)
async def multiple_question_read_post(
    request: Request,
    subject: Subject = Form(...),
    current_user=Depends(get_current_user),
):
    """
    瀏覽題目頁面的 POST 請求處理
    - 未登入使用者無法進入瀏覽題目頁面，會被導向首頁
    - 已登入使用者，且使用者角色為非老師，無法進入瀏覽題目頁面，會回應 403 錯誤
    - 已登入使用者，且使用者角色為老師，可提交瀏覽題目請求
    """
    # Check if user is teacher
    if not current_user:
        return _302_REDIRECT_TO_HOME

    if current_user.role != Role.TEACHER:
        return _403_NOT_A_TEACHER

    # Check if the question(s) to be viewed exist(s)
    questions = await QuestionCrud.get_by_subject(subject)
    if not questions:
        return templates.TemplateResponse(
            "question_read.html",
            {
                "request": request,
                "current_user": current_user,
                "error_multiple": f"該科目無題目",
            },
        )

    # Generate CSV content
    buffer = StringIO()
    csv_writer = writer(buffer)
    csv_writer.writerow(["subject", "filename", "answer"])
    for q in questions:
        filename = str(Path(q.image_path).name)[:6] + ".jpg"
        csv_writer.writerow([q.subject, filename, q.answer])
    buffer.seek(0)

    # Return CSV as downloadable file
    csv_filename = f"{subject}_questions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    csv_headers = {"Content-Disposition": f"attachment; filename={csv_filename}"}
    return StreamingResponse(
        buffer.getvalue(),
        media_type="text/csv",
        headers=csv_headers,
    )
