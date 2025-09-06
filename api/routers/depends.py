from datetime import datetime
from fastapi import Request

from crud.user import UserCrudManager

UserCrud = UserCrudManager()


# 檢查 token 是否過期
def is_token_expired(unix_timestamp: int):
    if unix_timestamp is None:
        return True
    return datetime.now() > datetime.fromtimestamp(unix_timestamp)


# 取得 session 資料
async def _get_session_data(request: Request):
    user_id = request.session.get("user_id")
    user = await UserCrud.get(user_id)
    token_exp = request.session.get("token_expiry")

    if not user or not token_exp or is_token_expired(token_exp):
        return None

    return user


# 取得目前登入使用者，若未登入則回傳 None
async def get_current_user(request: Request):
    user = await _get_session_data(request)
    return user
