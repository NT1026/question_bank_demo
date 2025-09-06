from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from random import sample

from .depends import get_current_user
from api.response import (
    _302_REDIRECT_TO_HOME,
    _403_NOT_A_STUDENT,
    _404_SUBJECT_NOT_FOUND,
    _404_EXAM_RECORD_NOT_FOUND,
)
from auth.image import generate_image_token
from crud.exam_record import ExamRecordCrudManager
from crud.question import QuestionCrudManager
from models.base import Role
from schemas import exam_record as ExamRecordSchema
from settings.subject import SUBJECT_EXAM_INFO

router = APIRouter()
templates = Jinja2Templates(directory="templates")

ExamRecordCrud = ExamRecordCrudManager()
QuestionCrud = QuestionCrudManager()


@router.get(
    "/exam/{subject_type}",
    response_class=HTMLResponse,
)
async def exam_page(
    request: Request,
    subject_type: str,
    current_user=Depends(get_current_user),
):
    """
    產生考卷頁面
    - 未登入使用者無法進入考試頁面，會被導向首頁
    - 已登入使用者，且使用者角色為非學生，無法進入考試頁面，會回應 403 錯誤
    - 已登入使用者，且使用者角色為學生，可進入考試頁面
    """
    # Check if user is student
    if not current_user:
        return _302_REDIRECT_TO_HOME

    if current_user.role != Role.STUDENT:
        return _403_NOT_A_STUDENT

    # If logged in, check subject is valid
    if subject_type not in SUBJECT_EXAM_INFO:
        return _404_SUBJECT_NOT_FOUND

    # Get 30 random questions from database
    subject = SUBJECT_EXAM_INFO[subject_type]["subject"]
    questions = await QuestionCrud.get_by_subject(subject)

    question_num = SUBJECT_EXAM_INFO[subject_type]["question_count"]
    selected_quesions = sample(questions, min(question_num, len(questions)))

    # Generate image token for each question
    for question in selected_quesions:
        question.token = generate_image_token(str(current_user.id), question.id)

    # Render exam.html
    return templates.TemplateResponse(
        "exam.html",
        {
            "request": request,
            "current_user": current_user,
            "subject": SUBJECT_EXAM_INFO[subject_type],
            "questions": selected_quesions,
        },
    )


@router.post(
    "/exam/submit/{subject_type}",
    response_class=HTMLResponse,
)
async def submit_exam(
    request: Request,
    subject_type: str,
    current_user=Depends(get_current_user),
):
    """
    提交考卷表單
    - 未登入使用者無法提交考卷，會被導向首頁
    - 已登入使用者，且使用者角色為非學生，無法提交考卷，會回應 403 錯誤
    - 已登入使用者，且使用者角色為學生，可提交考卷
    """
    # Check if user is student
    if not current_user:
        return _302_REDIRECT_TO_HOME

    if current_user.role != Role.STUDENT:
        return _403_NOT_A_STUDENT

    # If logged in, check subject is valid
    if subject_type not in SUBJECT_EXAM_INFO:
        return _404_SUBJECT_NOT_FOUND

    # Get user_answer list
    form = await request.form()
    user_answers = [
        {
            "question_id": k,
            "user_answer": "".join(sorted(list(item for item in v))),
        }
        for k, v in dict(form).items()
    ]

    # Check if user_answer is valid (Only Uppercase A, B, C, D)
    for item in user_answers:
        for c in item["user_answer"]:
            if c not in ["A", "B", "C", "D"]:
                item["user_answer"] = "輸入錯誤"

    # Create new exam record into database
    new_exam_record = ExamRecordSchema.ExamRecordCreate(
        subject_type=subject_type,
        user_answers=user_answers,
    )
    exam_record = await ExamRecordCrud.create(
        user_id=current_user.id,
        newExamRecord=new_exam_record,
    )

    # Redirect to exam record page
    return RedirectResponse(
        f"/student/exam/record/{exam_record.id}",
        status_code=status.HTTP_302_FOUND,
    )


@router.get(
    "/exam/record/{exam_record_id}",
    response_class=HTMLResponse,
)
async def get_exam_record(
    request: Request,
    exam_record_id: str,
    current_user=Depends(get_current_user),
):
    """
    測驗結果頁面
    - 未登入使用者無法進入測驗結果頁面，會被導向首頁
    - 已登入使用者，且使用者角色為非學生，無法進入測驗結果頁面，會回應 403 錯誤
    - 已登入使用者，且使用者角色為學生，可進入測驗結果頁面
    """
    # Check if user is student
    if not current_user:
        return _302_REDIRECT_TO_HOME

    if current_user.role != Role.STUDENT:
        return _403_NOT_A_STUDENT

    # Get exam_record data
    exam_record = await ExamRecordCrud.get(exam_record_id)
    if not exam_record or exam_record.user_id != current_user.id:
        return _404_EXAM_RECORD_NOT_FOUND

    # Rendering user_answers data
    rendered_user_answers = await ExamRecordCrud.get_user_answers_data(
        current_user_id=current_user.id,
        exam_record_id=exam_record_id,
    )

    # Render exam_result.html
    return templates.TemplateResponse(
        "exam_result.html",
        {
            "request": request,
            "current_user": current_user,
            "subject": SUBJECT_EXAM_INFO[exam_record.subject_type],
            "score": exam_record.score,
            "accuracy": f"{(exam_record.score / len(exam_record.user_answers)) * 100:.2f}%",
            "user_answers": rendered_user_answers,
        },
    )
