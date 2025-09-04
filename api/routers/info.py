from fastapi import APIRouter, status

from settings.configs import Settings

router = APIRouter()
settings = Settings()


@router.get(
    "",
    status_code=status.HTTP_200_OK,
)
async def info():
    return {
        "app_name": settings.APP_NAME,
        "host": settings.APP_HOST,
    }
