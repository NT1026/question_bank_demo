import uuid
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.mysql import crud_class_decorator
from models.user import User as UserModel
from schemas import user as UserSchema


@crud_class_decorator
class UserCrudManager:
    async def create(
        self,
        newUser: UserSchema.UserCreate,
        db_session: AsyncSession,
    ):
        # Check if user with the same username already exists
        stmt = select(UserModel).where(UserModel.username == newUser.username)
        result = await db_session.execute(stmt)
        exist = result.scalar_one_or_none()
        if exist:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="User already exists"
            )

        # Create new user
        newUser_dict = newUser.model_dump()
        user = UserModel(
            **newUser_dict,
            id=str(uuid.uuid4()),
            created_at=datetime.now(),
        )
        db_session.add(user)
        await db_session.commit()

        return user

    async def get(
        self,
        user_id: str,
        db_session: AsyncSession,
    ):
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await db_session.execute(stmt)
        user = result.scalar_one_or_none()

        return user

    async def get_all(
        self,
        db_session: AsyncSession,
    ):
        stmt = select(UserModel)
        result = await db_session.execute(stmt)
        users = result.scalars().all()

        return users

    async def update(
        self,
        user_id: str,
        updateUser: UserSchema.UserUpdate,
        db_session: AsyncSession,
    ):
        updateUser_dict = updateUser.model_dump(exclude_none=True)
        if updateUser_dict:
            stmt = (
                update(UserModel).where(UserModel.id == user_id).values(updateUser_dict)
            )
            await db_session.execute(stmt)
            await db_session.commit()

        return

    async def delete(
        self,
        user_id: str,
        db_session: AsyncSession,
    ):
        stmt = delete(UserModel).where(UserModel.id == user_id)
        await db_session.execute(stmt)
        await db_session.commit()

        return
