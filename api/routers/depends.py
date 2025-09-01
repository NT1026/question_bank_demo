from fastapi import HTTPException, status

from crud.question import QuestionCrudManager
from crud.user import UserCrudManager

QuestionCrud = QuestionCrudManager()
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
