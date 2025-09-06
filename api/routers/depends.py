from datetime import datetime
from fastapi import Request

from api.response import (
    _404_EXAM_RECORD_NOT_FOUND_API,
    _404_QUESTION_NOT_FOUND_API,
    _404_USER_NOT_FOUND_API,
)
from crud.question import QuestionCrudManager
from crud.exam_record import ExamRecordCrudManager
from crud.user import UserCrudManager

QuestionCrud = QuestionCrudManager()
ExamRecordCrud = ExamRecordCrudManager()
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


async def check_user_id(user_id: str):
    user = await UserCrud.get(user_id)
    if not user:
        raise _404_USER_NOT_FOUND_API

    return user_id


async def check_question_id(question_id: str):
    question = await QuestionCrud.get(question_id)
    if not question:
        raise _404_QUESTION_NOT_FOUND_API

    return question_id


async def check_exam_record_id(exam_record_id: str):
    exam_record = await ExamRecordCrud.get(exam_record_id)
    if not exam_record:
        raise _404_EXAM_RECORD_NOT_FOUND_API

    return exam_record
