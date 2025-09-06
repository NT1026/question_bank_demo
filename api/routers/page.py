import random

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from .depends import get_current_user
from auth.image import generate_image_token
from crud.exam_record import ExamRecordCrudManager
from crud.question import QuestionCrudManager
from schemas import exam_record as ExamRecordSchema

router = APIRouter()
templates = Jinja2Templates(directory="templates")

ExamRecordCrud = ExamRecordCrudManager()
QuestionCrud = QuestionCrudManager()

subject_dict = {
    "math_achievement": {
        "name": "math_achievement",
        "chinese_name": "數學成就測驗",
        "subject": "math",
        "question_count": 30,
        "time_limit": 3,
    },
    "nature_science_achievement": {
        "name": "nature_science_achievement",
        "chinese_name": "自然成就測驗",
        "subject": "nature_science",
        "question_count": 38,
        "time_limit": 76 * 60,
    },
    "math_aptitude": {
        "name": "math_aptitude",
        "chinese_name": "數學性向測驗",
        "subject": "math",
        "question_count": 20,
        "time_limit": 40 * 60,
    },
    "nature_science_aptitude": {
        "name": "nature_science_aptitude",
        "chinese_name": "自然性向測驗",
        "subject": "nature_science",
        "question_count": 50,
        "time_limit": 100 * 60,
    },
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
    - 已登入使用者可瀏覽首頁，並可進入考試頁面
    """
    # If not logged in, show index.html
    if not current_user:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
            },
        )

    # Get all exam record ids of current user
    exam_records = await ExamRecordCrud.get_by_user_id(current_user.id)
    exam_record_id_lists = {
        subject: [item.id for item in exam_records if item.subject_type == subject]
        for subject in subject_dict
    }

    # Get all exam records of current user
    exam_lists = {}
    for subject_type, ids in exam_record_id_lists.items():
        exam_lists[subject_type] = {
            "all_correct": 0,
            "all_questions": 0,
            "all_accuracy": "0.00%",
            "exam_records": [],
        }
        for exam_record_id in ids:
            exam_record = await ExamRecordCrud.get(exam_record_id)
            exam_lists[subject_type]["exam_records"].append(
                {
                    "exam_record_id": exam_record_id,
                    "score": exam_record.score,
                    "question_count": len(exam_record.user_answers),
                    "accuracy": f"{(exam_record.score / len(exam_record.user_answers)) * 100:.2f}%",
                    "created_at": exam_record.created_at,
                }
            )
        exam_lists[subject_type]["exam_records"].sort(
            key=lambda x: x["created_at"], reverse=True
        )
        exam_lists[subject_type]["all_correct"] = sum(
            item["score"] for item in exam_lists[subject_type]["exam_records"]
        )
        exam_lists[subject_type]["all_questions"] = sum(
            item["question_count"] for item in exam_lists[subject_type]["exam_records"]
        )
        if exam_lists[subject_type]["all_questions"] > 0:
            exam_lists[subject_type][
                "all_accuracy"
            ] = f"{(exam_lists[subject_type]['all_correct'] / exam_lists[subject_type]['all_questions']) * 100:.2f}%"

    # If logged in, show dashboard.html
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "current_user": current_user,
            "exam_lists": exam_lists,
        },
    )


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
    測驗 API
    - 未登入使用者無法進入考試頁面，會被導向首頁
    - 已登入使用者可進入考試頁面
    """
    # If not logged in, redirect to /
    if not current_user:
        return RedirectResponse(
            "/",
            status_code=status.HTTP_302_FOUND,
        )

    # If logged in, check subject is valid (math or nature_science)
    if subject_type not in subject_dict:
        return HTMLResponse(
            "該科目測驗不存在",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    # Get 30 random questions from database
    subject = subject_dict[subject_type]["subject"]
    questions = await QuestionCrud.get_by_subject(subject)

    question_num = subject_dict[subject_type]["question_count"]
    selected_quesions = random.sample(questions, min(question_num, len(questions)))

    # Generate image token for each question
    for question in selected_quesions:
        question.token = generate_image_token(str(current_user.id), question.id)

    # Show exam.html
    return templates.TemplateResponse(
        "exam.html",
        {
            "request": request,
            "current_user": current_user,
            "subject": subject_dict[subject_type],
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
    提交考卷 API
    - 未登入使用者無法提交考卷，會被導向首頁
    - 已登入使用者可提交考卷，並計算分數與答題結果
    """
    # If not logged in, redirect to /
    if not current_user:
        return RedirectResponse(
            "/",
            status_code=status.HTTP_302_FOUND,
        )

    # If logged in, check subject is valid (math or nature_science)
    if subject_type not in subject_dict:
        return HTMLResponse(
            "該科目測驗不存在",
            status_code=status.HTTP_404_NOT_FOUND,
        )

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

    return RedirectResponse(
        f"/exam/record/{exam_record.id}",
        status_code=status.HTTP_302_FOUND,
    )


@router.get(
    "/exam/record/{exam_record_id}",
    response_class=HTMLResponse,
)
async def submit_exam(
    request: Request,
    exam_record_id: str,
    current_user=Depends(get_current_user),
):
    # If not logged in, redirect to /
    if not current_user:
        return RedirectResponse(
            "/",
            status_code=status.HTTP_302_FOUND,
        )

    # Get exam_record data
    exam_record = await ExamRecordCrud.get(exam_record_id)
    if not exam_record or exam_record.user_id != current_user.id:
        return HTMLResponse(
            "該測驗紀錄不存在",
            status_code=status.HTTP_404_NOT_FOUND,
        )

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
            "subject": subject_dict[exam_record.subject_type],
            "score": exam_record.score,
            "accuracy": f"{(exam_record.score / len(exam_record.user_answers)) * 100:.2f}%",
            "user_answers": rendered_user_answers,
        },
    )
