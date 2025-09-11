from csv import DictReader, writer
from datetime import datetime
from fastapi import APIRouter, Depends, File, Form, Request, status, UploadFile
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from io import BytesIO, StringIO
from pathlib import Path
from shutil import copyfileobj
from uuid import uuid4
from zipfile import ZipFile

from .depends import get_current_user
from api.response import (
    _302_REDIRECT_TO_HOME,
    _403_NOT_A_TEACHER,
)
from crud.question import QuestionCrudManager
from models.base import Role, Subject
from settings.configs import Settings

router = APIRouter()
templates = Jinja2Templates(directory="templates")
settings = Settings()

QuestionCrud = QuestionCrudManager()


@router.get(
    "/question/create",
    response_class=HTMLResponse,
)
async def question_create(
    request: Request,
    current_user=Depends(get_current_user),
):
    """
    新增題目頁面
    - 未登入使用者無法進入新增題目頁面，會被導向首頁
    - 已登入使用者，且使用者角色為非老師，無法進入新增題目頁面，會回應 403 錯誤
    - 已登入使用者，且使用者角色為老師，可進入新增題目頁面
    """
    # Check if user is teacher
    if not current_user:
        return _302_REDIRECT_TO_HOME

    if current_user.role != Role.TEACHER:
        return _403_NOT_A_TEACHER

    # Render question_create.html
    return templates.TemplateResponse(
        "question_create.html",
        {
            "request": request,
            "current_user": current_user,
        },
    )


@router.post(
    "/question/create",
    response_class=HTMLResponse,
)
async def single_question_create_post(
    request: Request,
    file: UploadFile = File(...),
    answer: str = Form(...),
    current_user=Depends(get_current_user),
):
    """
    新增單題題目頁面的 POST 請求處理
    - 未登入使用者無法進入新增題目頁面，會被導向首頁
    - 已登入使用者，且使用者角色為非老師，無法進入新增題目頁面，會回應 403 錯誤
    - 已登入使用者，且使用者角色為老師，可提交新增單題題目請求
    """
    # Check if user is teacher
    if not current_user:
        return _302_REDIRECT_TO_HOME

    if current_user.role != Role.TEACHER:
        return _403_NOT_A_TEACHER

    # Check answer format is valid
    sorted_answer = "".join(sorted(list(item for item in answer.upper())))
    if (
        not sorted_answer
        or not all(c in "ABCD" for c in sorted_answer)
        or len(sorted_answer) > 4
    ):
        return templates.TemplateResponse(
            "question_create.html",
            {
                "request": request,
                "current_user": current_user,
                "error_single": "答案格式錯誤，請輸入 A/B/C/D 的組合，長度為 1~4 個字元",
            },
        )

    # File type check
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
            answer=sorted_answer,
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
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.post(
    "/questions/create",
    response_class=HTMLResponse,
)
async def multiple_questions_create_post(
    request: Request,
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
):
    # Check if user is teacher
    if not current_user:
        return _302_REDIRECT_TO_HOME

    if current_user.role != Role.TEACHER:
        return _403_NOT_A_TEACHER

    # File type check
    if not file.filename.endswith(".zip"):
        return templates.TemplateResponse(
            "question_create.html",
            {
                "request": request,
                "current_user": current_user,
                "error_multiple": "檔案格式錯誤，請上傳 ZIP 檔案",
            },
        )

    failed_to_add = []
    try:
        # Read zip file
        zip_data = await file.read()
        with ZipFile(BytesIO(zip_data)) as zip_file:
            # Extract CSV file
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
                    csv_image_name = row.get("filename")
                    answer = row.get("answer")

                    if not csv_image_name or not answer:
                        failed_to_add.append(f"{csv_image_name} (欄位缺失)")
                        continue

                    # Check answer format
                    sorted_answer = "".join(
                        sorted(list(item for item in answer.upper()))
                    )
                    if (
                        not sorted_answer
                        or not all(c in "ABCD" for c in sorted_answer)
                        or len(sorted_answer) > 4
                    ):
                        failed_to_add.append(f"{csv_image_name} (答案格式錯誤)")
                        continue

                    # Check duplicate
                    existing_question = await QuestionCrud.get_by_filename(
                        f"{Path(csv_image_name).stem}"
                    )
                    if existing_question:
                        failed_to_add.append(f"{csv_image_name} (題目已存在)")
                        continue

                    # Find image inside zip
                    zip_image_path = next(
                        (
                            name
                            for name in zip_file.namelist()
                            if Path(name).name == csv_image_name
                        ),
                        None,
                    )
                    if not zip_image_path:
                        failed_to_add.append(f"{csv_image_name} (找不到對應圖片檔)")
                        continue

                    # Save image to disk
                    is_math = csv_image_name.startswith("M")
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
                        / f"{Path(csv_image_name).stem}_{question_id}.jpg"
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
                        answer=sorted_answer,
                    )

                if failed_to_add:
                    failed_list = ",".join(failed_to_add)
                    return templates.TemplateResponse(
                        "question_create.html",
                        {
                            "request": request,
                            "current_user": current_user,
                            "error_multiple": f"以下題目新增失敗：{failed_list}",
                        },
                    )

                return templates.TemplateResponse(
                    "question_create.html",
                    {
                        "request": request,
                        "current_user": current_user,
                        "success_multiple": f"已新增題目：{file.filename}",
                    },
                )

    except Exception:
        return templates.TemplateResponse(
            "question_create.html",
            {
                "request": request,
                "current_user": current_user,
                "error_multiple": f"新增題目失敗",
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.get(
    "/question/read",
    response_class=HTMLResponse,
)
async def question_read(
    request: Request,
    current_user=Depends(get_current_user),
):
    """
    瀏覽題目頁面
    - 未登入使用者無法進入瀏覽題目頁面，會被導向首頁
    - 已登入使用者，且使用者角色為非老師，無法進入瀏覽題目頁面，會回應 403 錯誤
    - 已登入使用者，且使用者角色為老師，可進入瀏覽題目頁面
    """
    # Check if user is teacher
    if not current_user:
        return _302_REDIRECT_TO_HOME

    if current_user.role != Role.TEACHER:
        return _403_NOT_A_TEACHER

    # Render question_read.html
    return templates.TemplateResponse(
        "question_read.html",
        {
            "request": request,
            "current_user": current_user,
        },
    )


@router.post(
    "/question/read",
    response_class=HTMLResponse,
)
async def multiple_question_read_post(
    request: Request,
    subject: Subject = Form(...),
    current_user=Depends(get_current_user),
):
    """
    瀏覽題目頁面的 POST 請求處理
    - 未登入使用者無法進入瀏覽題目頁面，會被導向首頁
    - 已登入使用者，且使用者角色為非老師，無法進入瀏覽題目頁面，會回應 403 錯誤
    - 已登入使用者，且使用者角色為老師，可提交瀏覽題目請求
    """
    # Check if user is teacher
    if not current_user:
        return _302_REDIRECT_TO_HOME

    if current_user.role != Role.TEACHER:
        return _403_NOT_A_TEACHER

    # Check if the question(s) to be viewed exist(s)
    questions = await QuestionCrud.get_by_subject(subject)
    if not questions:
        return templates.TemplateResponse(
            "question_read.html",
            {
                "request": request,
                "current_user": current_user,
                "error": f"該科目無題目",
            },
        )

    # Generate CSV content
    buffer = StringIO()
    csv_writer = writer(buffer)
    csv_writer.writerow(["subject", "filename", "answer"])
    for q in questions:
        filename = str(Path(q.image_path).name)[: 6] + ".jpg"
        csv_writer.writerow(
            [q.subject, filename, q.answer]
        )
    buffer.seek(0)

    # Return CSV as downloadable file
    csv_filename = f"{subject}_questions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    csv_headers = {"Content-Disposition": f"attachment; filename={csv_filename}"}
    return StreamingResponse(
        buffer.getvalue(),
        media_type="text/csv",
        headers=csv_headers,
    )


@router.get(
    "/question/delete",
    response_class=HTMLResponse,
)
async def question_delete(
    request: Request,
    current_user=Depends(get_current_user),
):
    """
    刪除題目頁面
    - 未登入使用者無法進入刪除題目頁面，會被導向首頁
    - 已登入使用者，且使用者角色為非老師，無法進入刪除題目頁面，會回應 403 錯誤
    - 已登入使用者，且使用者角色為老師，可進入刪除題目頁面
    """
    # Check if user is teacher
    if not current_user:
        return _302_REDIRECT_TO_HOME

    if current_user.role != Role.TEACHER:
        return _403_NOT_A_TEACHER

    # Render question_delete.html
    return templates.TemplateResponse(
        "question_delete.html",
        {
            "request": request,
            "current_user": current_user,
        },
    )


@router.post(
    "/question/delete",
    response_class=HTMLResponse,
)
async def question_delete_post(
    request: Request,
    filename: str = Form(...),
    current_user=Depends(get_current_user),
):
    """
    刪除題目頁面的 POST 請求處理
    - 未登入使用者無法進入刪除題目頁面，會被導向首頁
    - 已登入使用者，且使用者角色為非老師，無法進入刪除題目頁面，會回應 403 錯誤
    - 已登入使用者，且使用者角色為老師，可提交刪除題目請求
    """
    # Check if user is teacher
    if not current_user:
        return _302_REDIRECT_TO_HOME

    if current_user.role != Role.TEACHER:
        return _403_NOT_A_TEACHER

    # Check if the question(s) to be deleted exist(s)
    questions_to_delete = await QuestionCrud.get_by_filename(filename)
    if not questions_to_delete:
        return templates.TemplateResponse(
            "question_delete.html",
            {
                "request": request,
                "current_user": current_user,
                "error": f"找不到該題目：{filename}",
            },
        )

    # Delete all questions with the given filename
    await QuestionCrud.delete_by_filename(filename)
    return templates.TemplateResponse(
        "question_delete.html",
        {
            "request": request,
            "current_user": current_user,
            "success": f"已刪除指定題目：{filename}",
        },
    )
