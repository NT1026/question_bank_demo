from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from .depends import get_current_user
from api.response import (
    _302_REDIRECT_TO_HOME,
    _302_REDIRECT_TO_STUDENT_DASHBOARD,
    _302_REDIRECT_TO_TEACHER_DASHBOARD,
    _403_NOT_A_STUDENT,
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


@router.get("/", response_class=HTMLResponse)
async def index_page(
    request: Request,
    current_user=Depends(get_current_user),
):
    """
    首頁 API
    - 未登入使用者可瀏覽首頁，但無法進入考試頁面
    - 已登入使用者，且角色為學生，可瀏覽首頁
    - 已登入使用者，且角色為老師，可瀏覽首頁
    """
    # If not logged in
    if not current_user:
        return templates.TemplateResponse("index.html", {"request": request})

    # If logged in
    if current_user.role == Role.STUDENT:
        return _302_REDIRECT_TO_STUDENT_DASHBOARD

    elif current_user.role == Role.TEACHER:
        return _302_REDIRECT_TO_TEACHER_DASHBOARD


@router.get("/student/dashboard", response_class=HTMLResponse)
async def student_dashboard(
    request: Request,
    current_user=Depends(get_current_user),
):
    """
    學生儀表板頁面
    - 未登入使用者無法進入學生儀表板，會被導向首頁
    - 已登入使用者，且使用者角色為非學生，無法進入學生儀表板，會回應 403 錯誤
    - 已登入使用者，且使用者角色為學生，可進入學生儀表板
    """
    # Check if user is student
    if not current_user:
        return _302_REDIRECT_TO_HOME

    if current_user.role != Role.STUDENT:
        return _403_NOT_A_STUDENT

    # Get all exam info of current user
    exam_records = await ExamRecordCrud.get_by_user_id(current_user.id)
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
            "student_info": current_user,
            "exam_lists": exam_lists,
        },
    )


@router.get("/teacher/dashboard", response_class=HTMLResponse)
async def teacher_dashboard(
    request: Request,
    current_user=Depends(get_current_user),
):
    """
    教師儀表板頁面
    - 未登入使用者無法進入教師儀表板，會被導向首頁
    - 已登入使用者，且使用者角色為非教師，無法進入教師儀表板，會回應 403 錯誤
    - 已登入使用者，且使用者角色為教師，可進入教師儀表板
    """
    # Check if user is teacher
    if not current_user:
        return _302_REDIRECT_TO_HOME

    if current_user.role != Role.TEACHER:
        return _403_NOT_A_TEACHER

    # Render dashboard_teacher.html
    return templates.TemplateResponse(
        "dashboard_teacher.html",
        {
            "request": request,
            "current_user": current_user,
        },
    )
