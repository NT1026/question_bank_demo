from csv import writer
from datetime import datetime
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from io import StringIO

from .depends import get_current_user
from api.response import (
    _302_REDIRECT_TO_HOME,
    _403_NOT_A_ADMIN_OR_TEACHER,
)
from crud.user import UserCrudManager
from models.base import Role
from utils.exam import get_exam_render_info

router = APIRouter()
templates = Jinja2Templates(directory="templates")

UserCrud = UserCrudManager()


@router.get("")
async def user_read(
    request: Request,
    current_user=Depends(get_current_user),
):
    # Check if not logged in
    if not current_user:
        return _302_REDIRECT_TO_HOME

    # Check if user is teacher or admin
    if current_user.role not in [Role.TEACHER, Role.ADMIN]:
        return _403_NOT_A_ADMIN_OR_TEACHER
    
    # Render user_read.html
    return templates.TemplateResponse(
        "user_read.html",
        {
            "request": request,
            "current_user": current_user,
        },
    )


@router.post("")
async def single_user_read_post(
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

    # Check if the user to be viewed exists
    user_to_read = await UserCrud.get_by_username(username)
    if not user_to_read:
        return templates.TemplateResponse(
            "user_read.html",
            {
                "request": request,
                "current_user": current_user,
                "error_single": "查無此使用者",
            },
        )

    # Check if the user to be viewed is a student
    if user_to_read.role != Role.STUDENT:
        return templates.TemplateResponse(
            "user_read.html",
            {
                "request": request,
                "current_user": current_user,
                "error_single": "無法讀取教師詳細資訊",
            },
        )

    # Render dashboard_student.html
    return templates.TemplateResponse(
        "dashboard_student.html",
        {
            "request": request,
            "current_user": current_user,
            "student_info": user_to_read,
            "exam_lists": await get_exam_render_info(user_to_read.id),
        },
    )


@router.post("/bulk")
async def multiple_user_read_post(
    current_user=Depends(get_current_user),
):
    # Check if not logged in
    if not current_user:
        return _302_REDIRECT_TO_HOME

    # Check if user is teacher or admin
    if current_user.role not in [Role.TEACHER, Role.ADMIN]:
        return _403_NOT_A_ADMIN_OR_TEACHER

    # Generate CSV content
    buffer = StringIO()
    csv_writer = writer(buffer)
    csv_writer.writerow(["username", "name", "role", "created_at"])

    all_users = await UserCrud.get_all()
    for user in all_users:
        csv_writer.writerow([user.username, user.name, user.role, user.created_at])

    buffer.seek(0)

    # Return CSV as downloadable file
    csv_filename = f"all_users_info_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    csv_headers = {"Content-Disposition": f"attachment; filename={csv_filename}"}
    return StreamingResponse(
        buffer.getvalue(),
        media_type="text/csv",
        headers=csv_headers,
    )
