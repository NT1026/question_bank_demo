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
    "/user/create",
    response_class=HTMLResponse,
)
async def user_create(
    request: Request,
    current_user=Depends(get_current_user),
):
    """
    新增使用者頁面
    - 未登入使用者無法進入新增使用者頁面，會被導向首頁
    - 已登入使用者，且使用者角色為非老師，無法進入新增使用者頁面，會回應 403 錯誤
    - 已登入使用者，且使用者角色為老師，可進入新增使用者頁面
    """
    # Check if user is logged in
    if not current_user:
        return _302_REDIRECT_TO_HOME

    # If logged in, check if user is teacher
    if current_user.role != Role.TEACHER:
        return _403_NOT_A_TEACHER

    return templates.TemplateResponse(
        "user_create.html",
        {
            "request": request,
            "current_user": current_user,
        },
    )


@router.get(
    "/user/read",
    response_class=HTMLResponse,
)
async def user_read(
    request: Request,
    current_user=Depends(get_current_user),
):
    """
    使用者列表頁面
    - 未登入使用者無法進入使用者列表頁面，會被導向首頁
    - 已登入使用者，且使用者角色為非老師，無法進入使用者列表頁面，會回應 403 錯誤
    - 已登入使用者，且使用者角色為老師，可進入使用者列表頁面
    """
    # Check if user is logged in
    if not current_user:
        return _302_REDIRECT_TO_HOME

    # If logged in, check if user is teacher
    if current_user.role != Role.TEACHER:
        return _403_NOT_A_TEACHER

    return templates.TemplateResponse(
        "user_read.html",
        {
            "request": request,
            "current_user": current_user,
        },
    )


@router.get(
    "/user/delete",
    response_class=HTMLResponse,
)
async def user_delete(
    request: Request,
    current_user=Depends(get_current_user),
):
    """
    刪除使用者頁面
    - 未登入使用者無法進入刪除使用者頁面，會被導向首頁
    - 已登入使用者，且使用者角色為非老師，無法進入刪除使用者頁面，會回應 403 錯誤
    - 已登入使用者，且使用者角色為老師，可進入刪除使用者頁面
    """
    # Check if user is logged in
    if not current_user:
        return _302_REDIRECT_TO_HOME

    # If logged in, check if user is teacher
    if current_user.role != Role.TEACHER:
        return _403_NOT_A_TEACHER

    return templates.TemplateResponse(
        "user_delete.html",
        {
            "request": request,
            "current_user": current_user,
        },
    )
