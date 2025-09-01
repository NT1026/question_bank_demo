from fastapi import HTTPException, status

from crud.user import UserCrudManager

UserCrud = UserCrudManager()


async def check_user_id(user_id: str):
    user = await UserCrud.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist",
        )

    return user_id
