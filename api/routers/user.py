from fastapi import APIRouter, Depends, HTTPException, status

from .depends import check_user_id
from crud.user import UserCrudManager
from schemas import user as UserSchema

router = APIRouter()
UserCrud = UserCrudManager()


@router.post(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def create_user(newUser: UserSchema.UserCreate):
    """
    用以下資訊建立新使用者：
    - username (身分證字號)
    - password
    - name
    - role
    - created_at
    """
    if await UserCrud.get(newUser.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        )

    # newUser.password = get_password_hash(newUser.password)
    await UserCrud.create(newUser)

    return


@router.get(
    "/{user_id}",
    response_model=UserSchema.UserRead,
    status_code=status.HTTP_200_OK,
)
async def read_user(user_id: str = Depends(check_user_id)):
    """
    根據 user_id 取得使用者資訊
    """
    user = await UserCrud.get(user_id)
    return user


@router.get(
    "",
    response_model=list[UserSchema.UserRead],
    status_code=status.HTTP_200_OK,
)
async def read_users():
    """
    取得所有使用者資訊
    """
    users = await UserCrud.get_all()
    return users


@router.put(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def update_user(
    updateUser: UserSchema.UserUpdate,
    user_id: str = Depends(check_user_id),
):
    """
    更新使用者資訊：
    - name
    """
    await UserCrud.update(user_id=user_id, updateUser=updateUser)
    return


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(user_id: str = Depends(check_user_id)):
    """
    根據 user_id 刪除使用者
    """
    await UserCrud.delete(user_id)
    return
