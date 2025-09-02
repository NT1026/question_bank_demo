from fastapi import APIRouter, Depends, status

from .depends import check_record_id, check_user_id
from crud.record import RecordCrudManager
from crud.user import UserCrudManager
from schemas import record as RecordSchema

router = APIRouter()
RecordCrud = RecordCrudManager()
UserCrud = UserCrudManager()


@router.post(
    "",
    response_model=RecordSchema.RecordRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_record(
    newRecord: RecordSchema.RecordCreate,
    user_id: str = Depends(check_user_id),
):
    """
    用以下資訊新增一次測驗紀錄：
    - subject
    - user_answers (包含 question_id, user_answer, answer 的 JSON 陣列)
    """
    record = await RecordCrud.create(
        user_id=user_id,
        newRecord=newRecord,
    )
    return record


@router.get(
    "/particular/{record_id}",
    response_model=RecordSchema.RecordRead,
    status_code=status.HTTP_200_OK,
)
async def read_record(record_id: str = Depends(check_record_id)):
    """
    根據 record_id 取得測驗紀錄
    """
    record = await RecordCrud.get(record_id)
    return record


@router.get(
    "",
    response_model=list[RecordSchema.RecordRead],
    status_code=status.HTTP_200_OK,
)
async def read_all_records():
    """
    取得所有測驗紀錄
    """
    records = await RecordCrud.get_all()
    return records


@router.get(
    "/particular_user/{user_id}",
    response_model=list[RecordSchema.RecordRead],
    status_code=status.HTTP_200_OK,
)
async def read_records_by_user_id(user_id: str = Depends(check_user_id)):
    """
    根據 user_id 取得該使用者的所有測驗紀錄
    """
    records = await RecordCrud.get_by_user_id(user_id)
    return records


@router.delete(
    "/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_record(record_id: str = Depends(check_record_id)):
    """
    根據 record_id 刪除測驗紀錄
    """
    await RecordCrud.delete(record_id)
    return
