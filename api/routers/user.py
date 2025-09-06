from fastapi import APIRouter, status

from api.response import (
    _409_USER_EXISTS_API,
)
from auth.passwd import get_password_hash
from crud.user import UserCrudManager
from schemas import user as UserSchema

router = APIRouter()
UserCrud = UserCrudManager()


@router.post(
    "",
    response_model=UserSchema.UserRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(newUser: UserSchema.UserCreate):
    """
    用以下資訊建立新使用者：
    - username (身分證字號)
    - password
    - name
    - role
    """
    # Check if user with the same username already exists
    exist = await UserCrud.get_by_username(newUser.username)
    if exist:
        raise _409_USER_EXISTS_API

    # Create new user
    newUser.password = get_password_hash(newUser.password)
    user = await UserCrud.create(newUser)
    return user


@router.get(
    "",
    response_model=list[UserSchema.UserRead],
    status_code=status.HTTP_200_OK,
)
async def read_all_users():
    """
    取得所有使用者資訊
    """
    users = await UserCrud.get_all()
    return users
