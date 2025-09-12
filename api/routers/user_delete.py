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
from crud.user import UserCrudManager
from models.base import Role

router = APIRouter()
templates = Jinja2Templates(directory="templates")

UserCrud = UserCrudManager()


@router.get("", response_class=HTMLResponse)
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


@router.post("", response_class=HTMLResponse)
async def single_user_delete_post(
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
                "error_single": f"找不到該使用者帳號：{username}",
            },
        )

    # Delete the user
    await UserCrud.delete_by_username(username)
    return templates.TemplateResponse(
        "user_delete.html",
        {
            "request": request,
            "current_user": current_user,
            "success_single": f"已刪除使用者帳號：{username}",
        },
    )


@router.post("/bulk", response_class=HTMLResponse)
async def multiple_user_delete_post(
    request: Request,
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
):
    """
    批次刪除使用者頁面的 POST 請求處理
    - 未登入使用者無法進入刪除使用者頁面，會被導向首頁
    - 已登入使用者，且使用者角色為非老師，無法進入刪除使用者頁面，會回應 403 錯誤
    - 已登入使用者，且使用者角色為老師，可提交批次刪除使用者請求
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

    success_usernames = []
    error_usernames = []

    for row in csv_reader:
        username = row.get("username")
        user_to_delete = await UserCrud.get_by_username(username)
        if user_to_delete:
            await UserCrud.delete_by_username(username)
            success_usernames.append(username)

        else:
            error_usernames.append(username)

    success_message = (
        (
            f"已刪除使用者帳號：{', '.join(success_usernames)}"
            if success_usernames
            else ""
        )
        if success_usernames
        else ""
    )

    error_message = (
        (f"找不到使用者帳號：{', '.join(error_usernames)}" if error_usernames else "")
        if error_usernames
        else ""
    )

    return templates.TemplateResponse(
        "user_delete.html",
        {
            "request": request,
            "current_user": current_user,
            "success_multiple": success_message,
            "error_multiple": error_message,
        },
    )
