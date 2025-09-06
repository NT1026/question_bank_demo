from fastapi import APIRouter, Depends, status

from .depends import check_exam_record_id, check_user_id
from crud.exam_record import ExamRecordCrudManager
from crud.user import UserCrudManager
from schemas import exam_record as ExamRecordSchema

router = APIRouter()
ExamRecordCrud = ExamRecordCrudManager()
UserCrud = UserCrudManager()


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
