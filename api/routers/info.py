from fastapi import APIRouter

from config import Settings

router = APIRouter()
settings = Settings()


@router.get("/info")
async def info():
    return {
        "app_name": settings.app_name,
        "host": settings.host,
    }
