from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from .depends import get_current_user
from api.response import (
    _302_REDIRECT_TO_HOME,
    _403_NOT_A_TEACHER,
)
from auth.passwd import get_password_hash
from crud.user import UserCrudManager
from models.base import Role
from schemas import user as UserSchema

router = APIRouter()
templates = Jinja2Templates(directory="templates")

UserCrud = UserCrudManager()


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
    # Check if user is teacher
    if not current_user:
        return _302_REDIRECT_TO_HOME

    if current_user.role != Role.TEACHER:
        return _403_NOT_A_TEACHER

    # Render user_create.html
    return templates.TemplateResponse(
        "user_create.html",
        {
            "request": request,
            "current_user": current_user,
        },
    )


@router.post(
    "/user/create",
    response_class=HTMLResponse,
)
async def user_create_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    name: str = Form(...),
    role: Role = Form(...),
    current_user=Depends(get_current_user),
):
    """
    新增使用者頁面的 POST 請求處理
    - 未登入使用者無法進入新增使用者頁面，會被導向首頁
    - 已登入使用者，且使用者角色為非老師，無法進入新增使用者頁面，會回應 403 錯誤
    - 已登入使用者，且使用者角色為老師，可提交新增使用者請求
    """
    # Check if user is teacher
    if not current_user:
        return _302_REDIRECT_TO_HOME

    if current_user.role != Role.TEACHER:
        return _403_NOT_A_TEACHER

    # Check if user with the same username already exists
    user_to_add = await UserCrud.get_by_username(username)
    if user_to_add:
        return templates.TemplateResponse(
            "user_create.html",
            {
                "request": request,
                "current_user": current_user,
                "error": f"使用者帳號 {username} 已存在",
            },
        )

    # Create new user
    newUser = UserSchema.UserCreate(
        username=username,
        password=password,
        name=name,
        role=role,
    )
    newUser.password = get_password_hash(newUser.password)
    await UserCrud.create(newUser)
    return templates.TemplateResponse(
        "user_create.html",
        {
            "request": request,
            "current_user": current_user,
            "success": f"已建立新使用者帳號：{username}",
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
    # Check if user is teacher
    if not current_user:
        return _302_REDIRECT_TO_HOME

    if current_user.role != Role.TEACHER:
        return _403_NOT_A_TEACHER

    # Render user_read.html
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
    # Check if user is teacher
    if not current_user:
        return _302_REDIRECT_TO_HOME

    if current_user.role != Role.TEACHER:
        return _403_NOT_A_TEACHER

    # Render user_delete.html
    return templates.TemplateResponse(
        "user_delete.html",
        {
            "request": request,
            "current_user": current_user,
        },
    )


@router.post(
    "/user/delete",
    response_class=HTMLResponse,
)
async def user_delete_post(
    request: Request,
    username: str = Form(...),
    current_user=Depends(get_current_user),
):
    """
    刪除使用者頁面的 POST 請求處理
    - 未登入使用者無法進入刪除使用者頁面，會被導向首頁
    - 已登入使用者，且使用者角色為非老師，無法進入刪除使用者頁面，會回應 403 錯誤
    - 已登入使用者，且使用者角色為老師，可提交刪除使用者請求
    """
    # Check if user is teacher
    if not current_user:
        return _302_REDIRECT_TO_HOME

    if current_user.role != Role.TEACHER:
        return _403_NOT_A_TEACHER

    # Check if the user to be deleted exists
    user_to_delete = await UserCrud.get_by_username(username)
    if not user_to_delete:
        return templates.TemplateResponse(
            "user_delete.html",
            {
                "request": request,
                "current_user": current_user,
                "error": f"找不到該使用者帳號：{username}",
            },
        )

    # Delete the user
    await UserCrud.delete_by_username(username)
    return templates.TemplateResponse(
        "user_delete.html",
        {
            "request": request,
            "current_user": current_user,
            "success": f"已刪除使用者帳號：{username}",
        },
    )
