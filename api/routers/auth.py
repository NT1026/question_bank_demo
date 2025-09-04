from datetime import datetime, timedelta
from fastapi import APIRouter, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse

from auth.passwd import verify_password
from crud.user import UserCrudManager

router = APIRouter()
UserCrud = UserCrudManager()


@router.post(
    "/login",
    response_class=HTMLResponse,
)
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    """
    登入 API
    - 輸入：
        - username：使用者名稱 / 身份證
        - password：密碼
    - 檢查使用者是否存在 (用 username / 身份證檢查) 且密碼正確
    """
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


@router.get(
    "/logout",
    response_class=HTMLResponse,
)
async def logout(request: Request):
    """
    登出 API
    - 清除 session
    """
    request.session.clear()
    resp = RedirectResponse(
        "/",
        status_code=status.HTTP_302_FOUND,
    )
    return resp
