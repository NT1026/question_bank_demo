from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from .depends import get_current_user
from api.response import (
    _302_REDIRECT_TO_HOME,
    _302_REDIRECT_TO_STUDENT_DASHBOARD,
    _302_REDIRECT_TO_TEACHER_DASHBOARD,
    _403_NOT_A_STUDENT,
    _403_NOT_A_ADMIN_OR_TEACHER,
)
from models.base import Role
from utils.exam import get_exam_render_info

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/")
async def index_page(
    request: Request,
    current_user=Depends(get_current_user),
):
    # Check if not logged in
    if not current_user:
        return templates.TemplateResponse("index.html", {"request": request})

    # Check user role
    if current_user.role == Role.STUDENT:
        return _302_REDIRECT_TO_STUDENT_DASHBOARD

    elif current_user.role == Role.TEACHER or current_user.role == Role.ADMIN:
        return _302_REDIRECT_TO_TEACHER_DASHBOARD


@router.get("/student/dashboard")
async def student_dashboard(
    request: Request,
    current_user=Depends(get_current_user),
):
    # Check if not logged in
    if not current_user:
        return _302_REDIRECT_TO_HOME

    # Check if user is student
    if current_user.role != Role.STUDENT:
        return _403_NOT_A_STUDENT

    # Render dashboard_student.html
    return templates.TemplateResponse(
        "dashboard_student.html",
        {
            "request": request,
            "current_user": current_user,
            "student_info": current_user,
            "exam_lists": await get_exam_render_info(current_user.id),
        },
    )


@router.get("/teacher/dashboard")
async def teacher_dashboard(
    request: Request,
    current_user=Depends(get_current_user),
):
    # Check if not logged in
    if not current_user:
        return _302_REDIRECT_TO_HOME

    # Check if user is teacher or admin
    if current_user.role not in [Role.TEACHER, Role.ADMIN]:
        return _403_NOT_A_ADMIN_OR_TEACHER

    # Render dashboard_teacher.html
    return templates.TemplateResponse(
        "dashboard_teacher.html",
        {
            "request": request,
            "current_user": current_user,
        },
    )
