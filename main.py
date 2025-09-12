from asyncio import run

from api import api_run
from auth.passwd import get_password_hash
from crud.user import UserCrudManager
from database.mysql import init_db, close_db, drop_all_tables
from models.base import Role
from models.user import Role
from schemas import user as UserSchema
from settings.configs import Settings

settings = Settings()
UserCrud = UserCrudManager()


async def create_admin_user():
    admin_user = UserSchema.UserCreate(
        username=settings.ADMIN_USERNAME,
        password=settings.ADMIN_PASSWORD,
        name="admin",
        role=Role.ADMIN,
    )
    admin_user.password = get_password_hash(admin_user.password)
    await UserCrud.create(admin_user)


async def main():
    await init_db()
    await create_admin_user()
    await api_run()
    await drop_all_tables()
    await close_db()


if __name__ == "__main__":
    run(main=main())
