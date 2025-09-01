from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.schema import CreateTable, DropTable


from models.base import Base
from models.user import User


engine = create_async_engine(
    url="mysql+aiomysql://root:password@localhost:8888/question_bank_system",
    echo=True,
    pool_pre_ping=True,
)

SessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
    autocommit=False,
)


@asynccontextmanager
async def get_db():
    async with SessionLocal() as db:
        async with db.begin():
            yield db


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    await engine.dispose()


async def drop_all_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


def db_session_decorator(func):
    async def wrapper(*args, **kwargs):
        async with get_db() as db_session:
            kwargs["db_session"] = db_session
            result = await func(*args, **kwargs)
            return result

    return wrapper


def crud_class_decorator(cls):
    for name, method in cls.__dict__.items():
        if callable(method):
            setattr(cls, name, db_session_decorator(method))

    return cls
