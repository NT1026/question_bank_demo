from fastapi import HTTPException, status

from crud.question import QuestionCrudManager
from crud.record import RecordCrudManager
from crud.user import UserCrudManager

QuestionCrud = QuestionCrudManager()
RecordCrud = RecordCrudManager()
UserCrud = UserCrudManager()


async def check_user_id(user_id: str):
    user = await UserCrud.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist",
        )

    return user_id


async def check_question_id(question_id: str):
    question = await QuestionCrud.get(question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question does not exist",
        )

    return question_id


async def check_record_id(record_id: str):
    record = await RecordCrud.get(record_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Record does not exist",
        )

    return record_id
