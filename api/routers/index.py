from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from .auth import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def index_page(request: Request):
    user = get_current_user(request)
    return templates.TemplateResponse("index.html", {"request": request, "user": user})
