from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

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
