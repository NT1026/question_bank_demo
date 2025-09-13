from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from uvicorn import Config, Server

from settings.configs import Settings
from .routers import (
    auth_page_router,
    exam_page_router,
    index_page_router,
    question_api_router,
    question_create_router,
    question_delete_router,
    question_read_router,
    user_api_router,
    user_create_router,
    user_delete_router,
    user_read_router,
)

app = FastAPI()
settings = Settings()

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Routers
app.include_router(index_page_router, tags=["Index Page"])
app.include_router(auth_page_router, tags=["Auth Page"])
app.include_router(exam_page_router, prefix="/exam", tags=["Exam Page"])

app.include_router(user_create_router, prefix="/user/create", tags=["User Create"])
app.include_router(user_read_router, prefix="/user/read", tags=["User Read"])
app.include_router(user_delete_router, prefix="/user/delete", tags=["User Delete"])

app.include_router(question_create_router, prefix="/question/create", tags=["Question Create"])
app.include_router(question_read_router, prefix="/question/read", tags=["Question Read"])
app.include_router(question_delete_router, prefix="/question/delete", tags=["Question Delete"])

app.include_router(user_api_router, prefix="/api/user", tags=["User"])
app.include_router(question_api_router, prefix="/api/question", tags=["Question"])

# CORS settings
origins = ["http://127.0.0.1"]  # domain name
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session Middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET_KEY,
    same_site="lax",
    https_only=True,
)


# Middleware
# @app.middleware("http")
# async def middleware_1(request: Request, call_next):
#     try:
#         response = await call_next(request)
#         return response
#     except Exception as e:
#         print(e)
#         return JSONResponse(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             content={"detail": "Internal Server Error"},
#         )


# Run FastAPI with Uvicorn
async def api_run():
    config = Config(app=app, host=settings.APP_HOST, port=settings.APP_PORT)
    server = Server(config=config)
    await server.serve()
