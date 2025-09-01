from asyncio import run

from api import api_run
from database.mysql import init_db, close_db, drop_all_tables


async def main():
    await init_db()
    await api_run()
    await drop_all_tables()
    await close_db()


if __name__ == "__main__":
    run(main=main())
