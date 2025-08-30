import uuid

from database.database import users
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

router = APIRouter()

# 測試 session
sessions = {}  # key: session_id, value: username

# 正式環境 session (redis)
# TODO


def get_current_user(request: Request):
    """
    取得目前登入的使用者 (非 API)
    - 從 cookie 取得 session_id，並從 sessions 中取得使用者資訊
    - 若無登入則回傳 None
    """
    session_id = request.cookies.get("session_id")
    if session_id and session_id in sessions:
        return sessions[session_id]
    return None


@router.post("/login")
async def login(user_id: str = Form(...), password: str = Form(...)):
    """
    登入 API
    - user_id: 使用者帳號 (身分證字號)
    - password: 使用者密碼
    - name: 使用者名稱
    """
    # Check if user exists
    user = None
    for u in users:
        if u["user_id"] == user_id and u["password"] == password:
            user = u
            break

    # Create session and set cookie
    if user:
        session_id = str(uuid.uuid4())
        sessions[session_id] = user
        resp = RedirectResponse("/", status_code=302)
        resp.set_cookie(key="session_id", value=session_id)

        # Login successful
        return resp

    # Login failed
    return HTMLResponse("登入失敗", status_code=401)


@router.get("/logout")
async def logout(request: Request):
    """
    登出 API
    - 主動清除 session 並刪除 cookie
    - 重定向到 index.html
    """
    session_id = request.cookies.get("session_id")
    if session_id and session_id in sessions:
        del sessions[session_id]
    resp = RedirectResponse("/", status_code=302)
    resp.delete_cookie("session_id")
    return resp
