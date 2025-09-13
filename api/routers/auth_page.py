from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Form, Request

from api.response import (
    _302_REDIRECT_TO_HOME,
    _401_LOGIN_FAILED,
)
from auth.passwd import verify_password
from .depends import get_current_user
from crud.user import UserCrudManager

router = APIRouter()
UserCrud = UserCrudManager()


def new_session(user_id: int):
    expiry = datetime.now() + timedelta(minutes=60)
    session = {
        "user_id": user_id,
        "token_expiry": int(expiry.timestamp()),
    }
    return session


@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    current_user=Depends(get_current_user),
):
    # Check if logged in
    if current_user:
        return _302_REDIRECT_TO_HOME

    # Check if user exists and password is correct
    user = await UserCrud.get_by_username(username)
    if not user or not verify_password(password, user.password):
        return _401_LOGIN_FAILED

    # Create session
    request.session.update(new_session(user.id))
    return _302_REDIRECT_TO_HOME


@router.get("/logout")
async def logout(
    request: Request,
    current_user=Depends(get_current_user),
):
    # Check if not logged in
    if not current_user:
        return _302_REDIRECT_TO_HOME

    # Clear session
    request.session.clear()
    return _302_REDIRECT_TO_HOME
