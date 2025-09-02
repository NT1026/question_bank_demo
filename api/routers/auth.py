from datetime import datetime, timedelta
from fastapi import APIRouter, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse

from auth.passwd import verify_password
from crud.user import UserCrudManager

router = APIRouter()
UserCrud = UserCrudManager()


@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    # Check if user exists and password is correct
    user = await UserCrud.get_by_username(username)
    if not user or not verify_password(password, user.password):
        return HTMLResponse(
            "Login Failed",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    # Create session
    new_session = {
        "user_id": user.id,
        "token_expiry": (datetime.now() + timedelta(hours=1)).timestamp(),
    }
    request.session.update(new_session)

    # Send session cookie to client
    return RedirectResponse(
        "/",
        status_code=status.HTTP_302_FOUND,
    )


@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    resp = RedirectResponse(
        "/",
        status_code=status.HTTP_302_FOUND,
    )
    return resp
