from fastapi import APIRouter

from settings.configs import Settings

router = APIRouter()
settings = Settings()


@router.get("")
async def info():
    return {
        "app_name": settings.APP_NAME,
        "host": settings.APP_HOST,
    }
