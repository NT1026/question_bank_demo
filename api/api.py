from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from uvicorn import Config, Server

from config import Settings
from .routers import (
    auth_router,
    exam_router,
    index_router,
    info_router,
)

app = FastAPI()
settings = Settings()

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Routers
app.include_router(info_router, prefix="/info", tags=["info"])
app.include_router(index_router, tags=["index.html"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(exam_router, prefix="/exam", tags=["exam"])

# CORS settings
origins = ["http://127.0.0.1"]  # domain name
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def api_run():
    config = Config(app=app, host=settings.host, port=settings.port)
    server = Server(config=config)
    await server.serve()
