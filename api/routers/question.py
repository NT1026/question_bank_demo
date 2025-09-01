from fastapi import APIRouter, Depends, status

from .depends import check_question_id
from crud.question import QuestionCrudManager
from schemas import question as QuestionSchema

router = APIRouter()
QuestionCrud = QuestionCrudManager()


@router.post(
    "",
    response_model=QuestionSchema.QuestionRead,
    status_code=status.HTTP_200_OK,
)
async def create_question(newQuestion: QuestionSchema.QuestionCreate):
    """
    用以下資訊建立新題目：
    - subject
    - image_path
    - answer
    """
    question = await QuestionCrud.create(newQuestion)
    return question


@router.get(
    "/{question_id}",
    response_model=QuestionSchema.QuestionRead,
    status_code=status.HTTP_200_OK,
)
async def read_question(question_id: str = Depends(check_question_id)):
    """
    根據 question_id 取得題目
    """
    question = await QuestionCrud.get(question_id)
    return question


@router.get(
    "",
    response_model=list[QuestionSchema.QuestionRead],
    status_code=status.HTTP_200_OK,
)
async def read_all_questions():
    """
    取得所有題目
    """
    questions = await QuestionCrud.get_all()
    return questions


@router.get(
    "/subject/{subject}",
    response_model=list[QuestionSchema.QuestionRead],
    status_code=status.HTTP_200_OK,
)
async def read_questions_by_subject(subject: str):
    """
    根據科目取得該科目所有題目
    """
    questions = await QuestionCrud.get_by_subject(subject)
    return questions


@router.delete(
    "/{question_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_question(question_id: str = Depends(check_question_id)):
    """
    根據 question_id 刪除題目
    """
    await QuestionCrud.delete(question_id)
    return
