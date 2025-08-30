import random

from database.database import questions_math_database, questions_science_database
from routers.auth import get_current_user

from fastapi import Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter

router = APIRouter()
templates = Jinja2Templates(directory="templates")

subjects_dict = {"math": "數學", "science": "自然"}


@router.get("/{subject}", response_class=HTMLResponse)
async def exam_page(request: Request, subject: str):
    """
    隨機出題 API
    - 分為數學、自然兩個科目
    - 每次隨機從題庫中抽取 30 題
    - 使用者必須登入才能進入考試頁面
    """
    # Check if user is logged in
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/", status_code=302)

    # Select subject
    if subject == "math":
        questions = questions_math_database
    elif subject == "science":
        questions = questions_science_database
    else:
        return HTMLResponse("科目不存在", status_code=404)

    # Randomly select 30 questions
    selected = random.sample(questions, min(30, len(questions)))

    # Render exam page
    return templates.TemplateResponse(
        "math.html",
        {
            "request": request,
            "questions": selected,
            "subject": subject,
            "subject_chinese": subjects_dict[subject],
        },
    )


@router.post("/submit/{subject}", response_class=HTMLResponse)
async def submit_exam(request: Request, subject: str):
    """
    提交考卷 API
    - 計算分數並回傳結果頁面
    - 使用者必須登入才能提交考卷
    - 回傳結果頁面包含：答對題數、總題數、每題答對與否
    """
    # Get answer form
    form = await request.form()
    print(form)

    # Check if user is logged in
    if subject == "math":
        questions = questions_math_database
    elif subject == "science":
        questions = questions_science_database
    else:
        return HTMLResponse("科目不存在", status_code=404)

    # Calculate score
    score = 0
    results = []
    for q in questions:
        correct_answer = q["answer"]
        user_answer = form.get(f"answer_{q['id']}")
        user_answer = user_answer.strip() if user_answer else ""

        is_correct = user_answer in ["1", "2", "3", "4"] and user_answer.strip() == str(
            correct_answer
        )
        if is_correct:
            score += 1

        results.append(
            {
                "id": q["id"],
                "image": q["image"],
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct,
            }
        )

    # Render result page
    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "score": score,
            "subject": subject,
            "subject_chinese": subjects_dict[subject],
            "results": results,
        },
    )
