from csv import DictReader
from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.templating import Jinja2Templates
from io import StringIO

from .depends import get_current_user
from api.response import (
    _302_REDIRECT_TO_HOME,
    _403_NOT_A_ADMIN_OR_TEACHER,
)
from auth.passwd import get_password_hash
from crud.user import UserCrudManager
from models.base import Role
from schemas import user as UserSchema

router = APIRouter()
templates = Jinja2Templates(directory="templates")

UserCrud = UserCrudManager()


@router.get("")
async def user_create(
    request: Request,
    current_user=Depends(get_current_user),
):
    # Check if not logged in
    if not current_user:
        return _302_REDIRECT_TO_HOME

    # Check if user is teacher or admin
    if current_user.role not in [Role.TEACHER, Role.ADMIN]:
        return _403_NOT_A_ADMIN_OR_TEACHER

    # Render user_create.html
    return templates.TemplateResponse(
        "user_create.html",
        {
            "request": request,
            "current_user": current_user,
        },
    )


@router.post("")
async def single_user_create_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    name: str = Form(...),
    role: Role = Form(...),
    current_user=Depends(get_current_user),
):
    # Check if not logged in
    if not current_user:
        return _302_REDIRECT_TO_HOME

    # Check if user is teacher or admin
    if current_user.role not in [Role.TEACHER, Role.ADMIN]:
        return _403_NOT_A_ADMIN_OR_TEACHER

    # Check if want to add an admin user
    if role == Role.ADMIN:
        return templates.TemplateResponse(
            "user_create.html",
            {
                "request": request,
                "current_user": current_user,
                "error_single": "無法新增管理員帳號",
            },
        )

    # Check if user with the same username already exists
    user_to_add = await UserCrud.get_by_username(username)
    if user_to_add:
        return templates.TemplateResponse(
            "user_create.html",
            {
                "request": request,
                "current_user": current_user,
                "error_single": f"使用者帳號 {username} 已存在",
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
            "success_single": f"已建立新使用者帳號：{username}",
        },
    )


@router.post("/bulk")
async def multiple_user_create_post(
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
            "user_create.html",
            {
                "request": request,
                "current_user": current_user,
                "error_multiple": "上傳檔案格式錯誤，請上傳 CSV 檔案",
            },
        )

    # Check CSV file content and create users
    try:
        content = await file.read()
        f = StringIO(content.decode("utf-8"))
        reader = DictReader(f)

        # Create users
        success_to_add = []
        fail_to_add = []
        for row in reader:
            username = row["username"].strip()
            password = row["password"].strip()
            name = row["name"].strip()
            role = row["role"].strip()

            # Check if user_to_add is admin
            if role == Role.ADMIN:
                fail_to_add.append(f"{username}(無法新增管理員帳號)")
                continue

            # Check if user with the same username already exists
            user_to_add = await UserCrud.get_by_username(username)
            if not user_to_add:
                newUser = UserSchema.UserCreate(
                    username=username,
                    password=password,
                    name=name,
                    role=role,
                )
                newUser.password = get_password_hash(newUser.password)
                await UserCrud.create(newUser)
                success_to_add.append(username)
            else:
                fail_to_add.append(username)

    except Exception:
        return templates.TemplateResponse(
            "user_create.html",
            {
                "request": request,
                "current_user": current_user,
                "error_multiple": "CSV 檔案格式錯誤，請確認檔案內容",
            },
        )

    # Render user_create.html
    success_message = (
        f"以下使用者新增成功：{', '.join(success_to_add)}" if success_to_add else ""
    )

    error_message = (
        (f"以下使用者新增失敗：{', '.join(fail_to_add)}") if fail_to_add else ""
    )

    return templates.TemplateResponse(
        "user_create.html",
        {
            "request": request,
            "current_user": current_user,
            "success_multiple": success_message,
            "error_multiple": error_message,
        },
    )
