from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from .depends import get_current_user
from api.response import (
    _302_REDIRECT_TO_HOME,
    _302_REDIRECT_TO_STUDENT_DASHBOARD,
    _302_REDIRECT_TO_TEACHER_DASHBOARD,
    _401_LOGIN_FAILED,
    _403_NOT_A_STUDENT,
    _403_NOT_A_TEACHER,
)
from auth.passwd import verify_password
from crud.exam_record import ExamRecordCrudManager
from crud.user import UserCrudManager
from models.base import Role
from settings.subject import SUBJECT_EXAM_INFO

router = APIRouter()
templates = Jinja2Templates(directory="templates")

ExamRecordCrud = ExamRecordCrudManager()
UserCrud = UserCrudManager()


async def get_exam_summary(ids):
    records = []
    all_correct = 0
    all_questions = 0

    for exam_id in ids:
        exam = await ExamRecordCrud.get(exam_id)
        records.append(
            {
                "exam_record_id": exam_id,
                "score": exam.score,
                "question_count": len(exam.user_answers),
                "accuracy": f"{(exam.score / len(exam.user_answers)) * 100:.2f}%",
                "created_at": exam.created_at,
            }
        )
        all_correct += exam.score
        all_questions += len(exam.user_answers)

    records.sort(key=lambda x: x["created_at"], reverse=True)
    all_accuracy = (
        f"{(all_correct / all_questions) * 100:.2f}%" if all_questions else "0.00%"
    )

    return {
        "all_correct": all_correct,
        "all_questions": all_questions,
        "all_accuracy": all_accuracy,
        "exam_records": records,
    }


@router.get(
    "/",
    response_class=HTMLResponse,
)
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
    # If not logged in, show index.html
    if not current_user:
        return templates.TemplateResponse("index.html", {"request": request})

    # If logged in and user is student, show dashboard.html
    if current_user.role == Role.STUDENT:
        return _302_REDIRECT_TO_STUDENT_DASHBOARD

    # If logged in and user is teacher, show dashboard.html
    elif current_user.role == Role.TEACHER:
        return _302_REDIRECT_TO_TEACHER_DASHBOARD


@router.get(
    "/student/dashboard",
    response_class=HTMLResponse,
)
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
    # Check if user is logged in
    if not current_user:
        return _302_REDIRECT_TO_HOME

    # If logged in, check if user is student
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

    return templates.TemplateResponse(
        "dashboard_student.html",
        {
            "request": request,
            "current_user": current_user,
            "exam_lists": exam_lists,
        },
    )


@router.get(
    "/teacher/dashboard",
    response_class=HTMLResponse,
)
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
    # Check if user is logged in
    if not current_user:
        return _302_REDIRECT_TO_HOME

    # If logged in, check if user is teacher
    if current_user.role != Role.TEACHER:
        return _403_NOT_A_TEACHER

    return templates.TemplateResponse(
        "dashboard_teacher.html",
        {
            "request": request,
            "current_user": current_user,
        },
    )


@router.post(
    "/login",
    response_class=HTMLResponse,
)
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    """
    登入 API
    - 輸入：
        - username：使用者名稱 / 身份證
        - password：密碼
    - 檢查使用者是否存在 (用 username / 身份證檢查) 且密碼正確
    """
    # Check if user exists and password is correct
    user = await UserCrud.get_by_username(username)
    if not user or not verify_password(password, user.password):
        return _401_LOGIN_FAILED

    # Create session
    new_session = {
        "user_id": user.id,
        "token_expiry": (datetime.now() + timedelta(hours=1)).timestamp(),
    }
    request.session.update(new_session)
    return _302_REDIRECT_TO_HOME


@router.get(
    "/logout",
    response_class=HTMLResponse,
)
async def logout(request: Request):
    """
    登出 API
    - 清除 session
    """
    request.session.clear()
    return _302_REDIRECT_TO_HOME
