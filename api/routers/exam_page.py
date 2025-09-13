from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from .depends import get_current_user
from api.response import (
    _302_REDIRECT_TO_HOME,
    _403_CANNOT_ACCESS_OTHER_USER_DATA,
    _403_NOT_A_STUDENT,
    _403_NOT_A_TEACHER_OR_STUDENT,
    _404_EXAM_RECORD_NOT_FOUND,
    _404_EXAM_TYPE_NOT_FOUND,
)
from crud.exam_record import ExamRecordCrudManager
from models.base import Role
from schemas import exam_record as ExamRecordSchema
from settings.subject import SUBJECT_EXAM_INFO
from utils.exam import random_choose_questions

router = APIRouter()
templates = Jinja2Templates(directory="templates")

ExamRecordCrud = ExamRecordCrudManager()


@router.get("/{exam_type}")
async def exam_page(
    request: Request,
    exam_type: str,
    current_user=Depends(get_current_user),
):
    # Check if not logged in
    if not current_user:
        return _302_REDIRECT_TO_HOME

    # Check if user is student
    if current_user.role != Role.STUDENT:
        return _403_NOT_A_STUDENT

    # Check exam_type is valid
    if exam_type not in SUBJECT_EXAM_INFO:
        return _404_EXAM_TYPE_NOT_FOUND

    # Render exam.html
    return templates.TemplateResponse(
        "exam.html",
        {
            "request": request,
            "current_user": current_user,
            "subject": SUBJECT_EXAM_INFO[exam_type],
            "questions": await random_choose_questions(exam_type, current_user.id),
        },
    )


@router.post("/submit/{exam_type}")
async def submit_exam(
    request: Request,
    exam_type: str,
    current_user=Depends(get_current_user),
):
    # Check if not logged in
    if not current_user:
        return _302_REDIRECT_TO_HOME

    # Check if user is student
    if current_user.role != Role.STUDENT:
        return _403_NOT_A_STUDENT

    # Check exam_type is valid
    if exam_type not in SUBJECT_EXAM_INFO:
        return _404_EXAM_TYPE_NOT_FOUND

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
        exam_type=exam_type,
        user_answers=user_answers,
    )
    exam_record = await ExamRecordCrud.create(
        user_id=current_user.id,
        newExamRecord=new_exam_record,
    )

    # Redirect to exam record page
    return RedirectResponse(
        f"/exam/record/{exam_record.id}",
        status_code=status.HTTP_302_FOUND,
    )


@router.get("/record/{exam_record_id}")
async def get_exam_record(
    request: Request,
    exam_record_id: str,
    current_user=Depends(get_current_user),
):
    # Check if not logged in
    if not current_user:
        return _302_REDIRECT_TO_HOME

    # Check if user is student or teacher
    allowed_roles = [Role.STUDENT, Role.TEACHER]
    if current_user.role not in allowed_roles:
        return _403_NOT_A_TEACHER_OR_STUDENT

    # Check exam_record_id is valid
    exam_record = await ExamRecordCrud.get(exam_record_id)
    if not exam_record:
        return _404_EXAM_RECORD_NOT_FOUND

    # Check if the exam_record belongs to the current user (if current_user == student)
    if current_user.role == Role.STUDENT and exam_record.user_id != current_user.id:
        return _403_CANNOT_ACCESS_OTHER_USER_DATA

    # Prepare data for rendering
    accuracy = (
        f"{(exam_record.score / len(exam_record.user_answers)) * 100:.2f}%"
        if exam_record.user_answers
        else "0.00%"
    )
    rendered_user_answers = await ExamRecordCrud.get_rendered_user_answers_data(
        user_id=current_user.id,
        exam_record_id=exam_record_id,
    )

    # Render exam_result.html
    return templates.TemplateResponse(
        "exam_result.html",
        {
            "request": request,
            "current_user": current_user,
            "subject": SUBJECT_EXAM_INFO[exam_record.exam_type],
            "score": exam_record.score,
            "accuracy": accuracy,
            "user_answers": rendered_user_answers,
        },
    )
