import uvicorn

from routers.auth import get_current_user
from routers.auth import router as auth_router
from routers.exam import router as exam_router

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# 正式環境
# app = FastAPI(
#     docs_url=None,
#     redoc_url=None,
#     openapi_url=None
# )

# 開發環境
app = FastAPI()

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(exam_router, prefix="/exam", tags=["exam"])

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# index.html
@app.get("/", response_class=HTMLResponse, tags=["index.html"])
async def index_page(request: Request):
    user = get_current_user(request)
    return templates.TemplateResponse("index.html", {"request": request, "user": user})


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=80, reload=True)
