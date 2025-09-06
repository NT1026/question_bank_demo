from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from .depends import get_current_user
from api.response import (
    _302_REDIRECT_TO_HOME,
    _403_NOT_A_TEACHER,
)
from models.base import Role

router = APIRouter()
templates = Jinja2Templates(directory="templates")


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
    # Check if user is logged in
    if not current_user:
        return _302_REDIRECT_TO_HOME

    # If logged in, check if user is teacher
    if current_user.role != Role.TEACHER:
        return _403_NOT_A_TEACHER

    return templates.TemplateResponse(
        "question_create.html",
        {
            "request": request,
            "current_user": current_user,
        },
    )


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
    # Check if user is logged in
    if not current_user:
        return _302_REDIRECT_TO_HOME

    # If logged in, check if user is teacher
    if current_user.role != Role.TEACHER:
        return _403_NOT_A_TEACHER

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
    # Check if user is logged in
    if not current_user:
        return _302_REDIRECT_TO_HOME

    # If logged in, check if user is teacher
    if current_user.role != Role.TEACHER:
        return _403_NOT_A_TEACHER

    return templates.TemplateResponse(
        "question_delete.html",
        {
            "request": request,
            "current_user": current_user,
        },
    )
