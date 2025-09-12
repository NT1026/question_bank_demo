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
from crud.exam_record import ExamRecordCrudManager
from crud.user import UserCrudManager
from models.base import Role
from settings.subject import SUBJECT_EXAM_INFO
from utils.exam import get_exam_summary

router = APIRouter()
templates = Jinja2Templates(directory="templates")

ExamRecordCrud = ExamRecordCrudManager()
UserCrud = UserCrudManager()


@router.get("", response_class=HTMLResponse)
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


@router.post("", response_class=HTMLResponse)
async def single_user_read_post(
    request: Request,
    username: str = Form(...),
    current_user=Depends(get_current_user),
):
    """
    學生儀表板頁面
    - 未登入使用者無法進入學生儀表板，會被導向首頁
    - 已登入使用者，且使用者角色為非學生，無法進入學生儀表板，會回應 403 錯誤
    - 已登入使用者，且使用者角色為學生，可進入學生儀表板
    """
    # Check if user is teacher
    if not current_user:
        return _302_REDIRECT_TO_HOME

    if current_user.role != Role.TEACHER:
        return _403_NOT_A_TEACHER

    # Check if the query user is a student
    student = await UserCrud.get_by_username(username)
    if not student:
        return templates.TemplateResponse(
            "user_read.html",
            {
                "request": request,
                "current_user": current_user,
                "error_single": "查無此使用者",
            },
        )

    if student.role != Role.STUDENT:
        return templates.TemplateResponse(
            "user_read.html",
            {
                "request": request,
                "current_user": current_user,
                "error_single": "無法讀取教師詳細資訊",
            },
        )

    # Get all exam info of current student
    exam_records = await ExamRecordCrud.get_by_user_id(student.id)
    exam_lists = {
        subject_type: await get_exam_summary(
            [item.id for item in exam_records if item.subject_type == subject_type]
        )
        for subject_type in SUBJECT_EXAM_INFO
    }

    # Render dashboard_student.html
    return templates.TemplateResponse(
        "dashboard_student.html",
        {
            "request": request,
            "current_user": current_user,
            "student_info": student,
            "exam_lists": exam_lists,
        },
    )


@router.post("/bulk", response_class=HTMLResponse)
async def multiple_user_read_post(
    request: Request,
    current_user=Depends(get_current_user),
):
    """
    查詢多位使用者資訊，並輸出成 csv
    - 未登入使用者無法進入使用者列表頁面，會被導向首頁
    - 已登入使用者，且使用者角色為非老師，無法進入使用者列表頁面，會回應 403 錯誤
    - 已登入使用者，且使用者角色為老師，可進入使用者列表頁面
    """
    # Check if user is teacher
    if not current_user:
        return _302_REDIRECT_TO_HOME

    if current_user.role != Role.TEACHER:
        return _403_NOT_A_TEACHER

    # Check if the user(s) to be viewed exist(s)
    all_users = await UserCrud.get_all()

    # Generate CSV content
    buffer = StringIO()
    csv_writer = writer(buffer)
    csv_writer.writerow(["username", "name", "role", "created_at"])
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
