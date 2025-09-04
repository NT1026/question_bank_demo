from fastapi import APIRouter, Depends, status

from .depends import check_exam_record_id, check_user_id
from crud.exam_record import ExamRecordCrudManager
from crud.user import UserCrudManager
from schemas import exam_record as ExamRecordSchema

router = APIRouter()
ExamRecordCrud = ExamRecordCrudManager()
UserCrud = UserCrudManager()


@router.post(
    "",
    response_model=ExamRecordSchema.ExamRecordRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_exam_record(
    newExamRecord: ExamRecordSchema.ExamRecordCreate,
    user_id: str = Depends(check_user_id),
):
    """
    用以下資訊新增一次測驗紀錄：
    - subject
    - user_answers (包含 question_id, user_answer 的 JSON 陣列)
    """
    exam_record = await ExamRecordCrud.create(
        user_id=user_id,
        newExamRecord=newExamRecord,
    )
    return exam_record


@router.get(
    "/particular/{exam_record_id}",
    response_model=ExamRecordSchema.ExamRecordRead,
    status_code=status.HTTP_200_OK,
)
async def read_exam_record(exam_record_id: str = Depends(check_exam_record_id)):
    """
    根據 exam_record_id 取得測驗紀錄
    """
    exam_record = await ExamRecordCrud.get(exam_record_id)
    return exam_record


@router.get(
    "",
    response_model=list[ExamRecordSchema.ExamRecordRead],
    status_code=status.HTTP_200_OK,
)
async def read_all_exam_records():
    """
    取得所有測驗紀錄
    """
    exam_records = await ExamRecordCrud.get_all()
    return exam_records


@router.get(
    "/particular_user/{user_id}",
    response_model=list[ExamRecordSchema.ExamRecordRead],
    status_code=status.HTTP_200_OK,
)
async def read_exam_records_by_user_id(user_id: str = Depends(check_user_id)):
    """
    根據 user_id 取得該使用者的所有測驗紀錄
    """
    exam_records = await ExamRecordCrud.get_by_user_id(user_id)
    return exam_records


@router.delete(
    "/{exam_record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_exam_record(exam_record_id: str = Depends(check_exam_record_id)):
    """
    根據 exam_record_id 刪除測驗紀錄
    """
    await ExamRecordCrud.delete(exam_record_id)
    return
