from sqlalchemy import select, delete
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
        user = UserModel(
            username=newUser.username,
            password=newUser.password,
            name=newUser.name,
            role=newUser.role,
        )
        db_session.add(user)
        await db_session.commit()

        return user

    async def get_all(
        self,
        db_session: AsyncSession,
    ):
        stmt = select(UserModel)
        result = await db_session.execute(stmt)
        users = result.scalars().all()

        return users

    async def get(
        self,
        user_id: str,
        db_session: AsyncSession,
    ):
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await db_session.execute(stmt)
        user = result.scalar_one_or_none()

        return user

    async def get_by_username(
        self,
        username: str,
        db_session: AsyncSession,
    ):
        stmt = select(UserModel).where(UserModel.username == username)
        result = await db_session.execute(stmt)
        user = result.scalar_one_or_none()

        return user

    async def delete(
        self,
        user_id: str,
        db_session: AsyncSession,
    ):
        stmt = delete(UserModel).where(UserModel.id == user_id)
        await db_session.execute(stmt)
        await db_session.commit()

        return
