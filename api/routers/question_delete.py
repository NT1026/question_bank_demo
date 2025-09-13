from csv import DictReader
from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.templating import Jinja2Templates
from io import StringIO

from .depends import get_current_user
from api.response import (
    _302_REDIRECT_TO_HOME,
    _403_NOT_A_ADMIN_OR_TEACHER,
)
from crud.question import QuestionCrudManager
from models.base import Role

router = APIRouter()
templates = Jinja2Templates(directory="templates")

QuestionCrud = QuestionCrudManager()


@router.get("")
async def question_delete(
    request: Request,
    current_user=Depends(get_current_user),
):
    # Check if not logged in
    if not current_user:
        return _302_REDIRECT_TO_HOME

    # Check if user is teacher or admin
    if current_user.role not in [Role.TEACHER, Role.ADMIN]:
        return _403_NOT_A_ADMIN_OR_TEACHER

    # Render question_delete.html
    return templates.TemplateResponse(
        "question_delete.html",
        {
            "request": request,
            "current_user": current_user,
        },
    )


@router.post("")
async def single_question_delete_post(
    request: Request,
    filename: str = Form(...),
    current_user=Depends(get_current_user),
):
    # Check if not logged in
    if not current_user:
        return _302_REDIRECT_TO_HOME

    # Check if user is teacher or admin
    if current_user.role not in [Role.TEACHER, Role.ADMIN]:
        return _403_NOT_A_ADMIN_OR_TEACHER

    # Check if question_to_delete exist
    question_to_delete = await QuestionCrud.get_by_filename(filename)
    if not question_to_delete:
        return templates.TemplateResponse(
            "question_delete.html",
            {
                "request": request,
                "current_user": current_user,
                "error_single": f"找不到該題目：{filename}",
            },
        )

    # Delete the question with the given filename
    await QuestionCrud.delete_by_filename(filename)
    return templates.TemplateResponse(
        "question_delete.html",
        {
            "request": request,
            "current_user": current_user,
            "success_single": f"已刪除指定題目：{filename}",
        },
    )


@router.post("/bulk")
async def multiple_question_delete_post(
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

    # Check CSV file content and delete questions
    try:
        content = await file.read()
        decoded_content = content.decode("utf-8")
        csv_reader = DictReader(StringIO(decoded_content))

        success_questions = []
        error_questions = []

        for row in csv_reader:
            serial_number = row["serial_number"].strip()

            question_to_delete = await QuestionCrud.get_by_filename(serial_number)
            if question_to_delete:
                await QuestionCrud.delete_by_filename(serial_number)
                success_questions.append(serial_number)

            else:
                error_questions.append(serial_number)

    except Exception:
        return templates.TemplateResponse(
            "question_delete.html",
            {
                "request": request,
                "current_user": current_user,
                "error_multiple": "CSV 檔案內容錯誤，請確認後重新上傳",
            },
        )

    success_message = (
        f"已刪除題目：{', '.join(success_questions)}" if success_questions else ""
    )

    error_message = (
        f"找不到以下題目：{', '.join(error_questions)}" if error_questions else ""
    )

    return templates.TemplateResponse(
        "question_delete.html",
        {
            "request": request,
            "current_user": current_user,
            "success_multiple": success_message,
            "error_multiple": error_message,
        },
    )
