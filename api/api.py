from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from uvicorn import Config, Server

from settings.configs import Settings
from .routers import (
    index_page_router,
    question_router,
    student_page_router,
    teacher_question_page_router,
    teacher_user_page_router,
    user_router,
)

app = FastAPI()
settings = Settings()

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Routers
app.include_router(index_page_router, tags=["Index Page"])
app.include_router(student_page_router, prefix="/student", tags=["Student Page"])
app.include_router(teacher_user_page_router, prefix="/teacher", tags=["Teacher Page"])
app.include_router(teacher_question_page_router, prefix="/teacher", tags=["Teacher Page"])
app.include_router(user_router, prefix="/api/user", tags=["User"])
app.include_router(question_router, prefix="/api/question", tags=["Question"])

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
