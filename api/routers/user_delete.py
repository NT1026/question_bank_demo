from csv import DictReader
from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.templating import Jinja2Templates
from io import StringIO

from .depends import get_current_user
from api.response import (
    _302_REDIRECT_TO_HOME,
    _403_NOT_A_ADMIN_OR_TEACHER,
)
from crud.user import UserCrudManager
from models.base import Role
from settings.configs import Settings

router = APIRouter()
settings = Settings()
templates = Jinja2Templates(directory="templates")

UserCrud = UserCrudManager()


@router.get("")
async def user_delete(
    request: Request,
    current_user=Depends(get_current_user),
):
    # Check if not logged in
    if not current_user:
        return _302_REDIRECT_TO_HOME

    # Check if user is teacher or admin
    if current_user.role not in [Role.TEACHER, Role.ADMIN]:
        return _403_NOT_A_ADMIN_OR_TEACHER

    # Render user_delete.html
    return templates.TemplateResponse(
        "user_delete.html",
        {
            "request": request,
            "current_user": current_user,
        },
    )


@router.post("")
async def single_user_delete_post(
    request: Request,
    username: str = Form(...),
    current_user=Depends(get_current_user),
):
    # Check if not logged in
    if not current_user:
        return _302_REDIRECT_TO_HOME

    # Check if user is teacher or admin
    if current_user.role not in [Role.TEACHER, Role.ADMIN]:
        return _403_NOT_A_ADMIN_OR_TEACHER

    # Prevent deletion of admin account
    if username == settings.ADMIN_USERNAME:
        return templates.TemplateResponse(
            "user_delete.html",
            {
                "request": request,
                "current_user": current_user,
                "error_single": "無法刪除管理者帳號",
            },
        )

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


@router.post("/bulk")
async def multiple_user_delete_post(
    request: Request,
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
):
    # Check if not logged in
    if not current_user:
        return _302_REDIRECT_TO_HOME

    # Check if user is teacher or admin
    if current_user.role not in [Role.TEACHER, Role.ADMIN]:
        return _403_NOT_A_ADMIN_OR_TEACHER

    # Check if the uploaded file is a CSV file
    if file.content_type != "text/csv":
        return templates.TemplateResponse(
            "user_delete.html",
            {
                "request": request,
                "current_user": current_user,
                "error_multiple": "上傳檔案格式錯誤，請上傳 CSV 檔案",
            },
        )

    # Check CSV file content and delete users
    try:
        content = await file.read()
        decoded_content = content.decode("utf-8")
        csv_reader = DictReader(StringIO(decoded_content))

        success_usernames = []
        error_usernames = []

        for row in csv_reader:
            username = row["username"].strip()

            # Prevent deletion of admin account
            if username == settings.ADMIN_USERNAME:
                error_usernames.append(username)
                continue

            user_to_delete = await UserCrud.get_by_username(username)
            if user_to_delete:
                await UserCrud.delete_by_username(username)
                success_usernames.append(username)

            else:
                error_usernames.append(username)

    except Exception:
        return templates.TemplateResponse(
            "user_delete.html",
            {
                "request": request,
                "current_user": current_user,
                "error_multiple": "CSV 檔案內容錯誤，請確認檔案格式正確",
            },
        )

    success_message = (
        f"已刪除使用者帳號：{', '.join(success_usernames)}" if success_usernames else ""
    )

    error_message = (
        (f"找不到使用者帳號：{', '.join(error_usernames)}") if error_usernames else ""
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
