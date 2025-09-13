from csv import DictReader
from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.templating import Jinja2Templates
from io import BytesIO, StringIO
from pathlib import Path
from shutil import copyfileobj
from uuid import uuid4
from zipfile import ZipFile

from .depends import get_current_user
from api.response import (
    _302_REDIRECT_TO_HOME,
    _403_NOT_A_ADMIN_OR_TEACHER,
)
from crud.question import QuestionCrudManager
from models.base import Role
from settings.configs import Settings
from utils.question import is_invalid_answer_format, sorted_answer

router = APIRouter()
templates = Jinja2Templates(directory="templates")
settings = Settings()

QuestionCrud = QuestionCrudManager()


@router.get("")
async def question_create(
    request: Request,
    current_user=Depends(get_current_user),
):
    # Check if not logged in
    if not current_user:
        return _302_REDIRECT_TO_HOME

    # Check if user is teacher or admin
    if current_user.role not in [Role.TEACHER, Role.ADMIN]:
        return _403_NOT_A_ADMIN_OR_TEACHER

    # Render question_create.html
    return templates.TemplateResponse(
        "question_create.html",
        {
            "request": request,
            "current_user": current_user,
        },
    )


@router.post("")
async def single_question_create_post(
    request: Request,
    file: UploadFile = File(...),
    answer: str = Form(...),
    current_user=Depends(get_current_user),
):
    # Check if not logged in
    if not current_user:
        return _302_REDIRECT_TO_HOME

    # Check if user is teacher or admin
    if current_user.role not in [Role.TEACHER, Role.ADMIN]:
        return _403_NOT_A_ADMIN_OR_TEACHER

    # Check if answer format is valid
    if is_invalid_answer_format(answer):
        return templates.TemplateResponse(
            "question_create.html",
            {
                "request": request,
                "current_user": current_user,
                "error_single": "答案格式錯誤，請輸入 A/B/C/D 的組合，長度為 1~4 個字元",
            },
        )

    # Check if file is JPG
    if file.content_type not in ["image/jpeg"]:
        return templates.TemplateResponse(
            "question_create.html",
            {
                "request": request,
                "current_user": current_user,
                "error_single": "檔案格式錯誤，請上傳 JPG 檔案",
            },
        )

    # Check if the question to be created already exists
    existing_question = await QuestionCrud.get_by_filename(
        f"{Path(file.filename).stem}"
    )
    if existing_question:
        return templates.TemplateResponse(
            "question_create.html",
            {
                "request": request,
                "current_user": current_user,
                "error_single": f"題目已存在：{file.filename}",
            },
        )

    # Write file to disk
    try:
        is_math = file.filename.startswith("M")
        subject = "math" if is_math else "nature_science"
        subject_folder = (
            settings.MATH_DIRNAME if is_math else settings.NATURE_SCIENCE_DIRNAME
        )
        question_id = str(uuid4())

        base_path = Path(settings.PROTECTED_IMG_DIR)
        base_path.mkdir(parents=True, exist_ok=True)
        (base_path / subject_folder).mkdir(parents=True, exist_ok=True)

        image_path = (
            base_path / subject_folder / f"{Path(file.filename).stem}_{question_id}.jpg"
        )
        with image_path.open("wb") as f:
            copyfileobj(file.file, f)

        # Write into database
        await QuestionCrud.create(
            id=question_id,
            subject=subject,
            image_path=str(image_path),
            answer=sorted_answer(answer),
        )

        return templates.TemplateResponse(
            "question_create.html",
            {
                "request": request,
                "current_user": current_user,
                "success_single": f"已新增題目：{file.filename}",
            },
        )

    except Exception:
        return templates.TemplateResponse(
            "question_create.html",
            {
                "request": request,
                "current_user": current_user,
                "error_single": f"新增題目失敗：{file.filename}",
            },
        )


@router.post("/bulk")
async def multiple_questions_create_post(
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

    # Check if file is zip
    if not file.filename.endswith(".zip"):
        return templates.TemplateResponse(
            "question_create.html",
            {
                "request": request,
                "current_user": current_user,
                "error_multiple": "檔案格式錯誤，請上傳 ZIP 檔案",
            },
        )

    success_to_add = []
    failed_to_add = []
    try:
        zip_data = await file.read()
        with ZipFile(BytesIO(zip_data)) as zip_file:
            # Check if zip contains a CSV file
            csv_filename = next(
                (name for name in zip_file.namelist() if name.endswith(".csv")),
                None,
            )
            if not csv_filename:
                return templates.TemplateResponse(
                    "question_create.html",
                    {
                        "request": request,
                        "current_user": current_user,
                        "error_multiple": "ZIP 壓縮檔中找不到 CSV 檔案",
                    },
                )

            with zip_file.open(csv_filename) as csv_file:
                csv_content = StringIO(csv_file.read().decode("utf-8"))
                csv_reader = DictReader(csv_content)

                for row in csv_reader:
                    csv_filename = row["filename"].strip()
                    answer = row["answer"].strip()

                    # Check if answer format is valid
                    if is_invalid_answer_format(answer):
                        failed_to_add.append(f"{csv_filename}(答案格式錯誤)")
                        continue

                    # Check if question already exists
                    existing_question = await QuestionCrud.get_by_filename(
                        f"{Path(csv_filename).stem}"
                    )
                    if existing_question:
                        failed_to_add.append(f"{csv_filename}(題目已存在)")
                        continue

                    # Check if image exists in zip
                    zip_image_path = next(
                        (
                            name
                            for name in zip_file.namelist()
                            if Path(name).name == csv_filename
                        ),
                        None,
                    )
                    if not zip_image_path:
                        failed_to_add.append(f"{csv_filename}(找不到對應圖片檔)")
                        continue

                    # Save image to disk
                    is_math = csv_filename.startswith("M")
                    subject = "math" if is_math else "nature_science"
                    subject_folder = (
                        settings.MATH_DIRNAME
                        if is_math
                        else settings.NATURE_SCIENCE_DIRNAME
                    )
                    question_id = str(uuid4())

                    base_path = Path(settings.PROTECTED_IMG_DIR)
                    base_path.mkdir(parents=True, exist_ok=True)
                    (base_path / subject_folder).mkdir(parents=True, exist_ok=True)

                    final_image_path = (
                        base_path
                        / subject_folder
                        / f"{Path(csv_filename).stem}_{question_id}.jpg"
                    )

                    with zip_file.open(zip_image_path) as src, final_image_path.open(
                        "wb"
                    ) as dst:
                        copyfileobj(src, dst)

                    # Write into database
                    await QuestionCrud.create(
                        id=question_id,
                        subject=subject,
                        image_path=str(final_image_path),
                        answer=sorted_answer(answer),
                    )
                    success_to_add.append(csv_filename)

    except Exception:
        return templates.TemplateResponse(
            "question_create.html",
            {
                "request": request,
                "current_user": current_user,
                "error_multiple": f"新增題目失敗",
            },
        )

    success_message = (
        f"已新增題目：{', '.join(success_to_add)}" if success_to_add else ""
    )
    failed_message = (
        f"新增失敗題目：{', '.join(failed_to_add)}" if failed_to_add else ""
    )

    return templates.TemplateResponse(
        "question_create.html",
        {
            "request": request,
            "current_user": current_user,
            "success_multiple": success_message,
            "error_multiple": failed_message,
        },
    )