from fastapi import HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse

# Page Responses
_302_REDIRECT_TO_HOME = RedirectResponse(
    "/",
    status_code=status.HTTP_302_FOUND,
)

_302_REDIRECT_TO_STUDENT_DASHBOARD = RedirectResponse(
    "/student/dashboard",
    status_code=status.HTTP_302_FOUND,
)

_302_REDIRECT_TO_TEACHER_DASHBOARD = RedirectResponse(
    "/teacher/dashboard",
    status_code=status.HTTP_302_FOUND,
)

_401_LOGIN_FAILED = HTMLResponse(
    "登入失敗",
    status_code=status.HTTP_401_UNAUTHORIZED,
)

_403_NOT_A_STUDENT = HTMLResponse(
    "您的角色非學生，無法使用該功能",
    status_code=status.HTTP_403_FORBIDDEN,
)

_403_NOT_A_TEACHER = HTMLResponse(
    "您的角色非教師，無法使用該功能",
    status_code=status.HTTP_403_FORBIDDEN,
)

_404_SUBJECT_NOT_FOUND = HTMLResponse(
    "該科目不存在",
    status_code=status.HTTP_404_NOT_FOUND,
)

_404_EXAM_RECORD_NOT_FOUND = HTMLResponse(
    "該測驗紀錄不存在",
    status_code=status.HTTP_404_NOT_FOUND,
)

# User API Responses
_404_USER_NOT_FOUND_API = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="User does not exist",
)

_409_USER_EXISTS_API = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="User already exists",
)

# Question API Responses
_400_INVALID_ANSWER_FORMAT_API = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Answer must be combination of A/B/C/D, 1~4 characters",
)

_400_INVALID_FILE_TYPE_API = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="File must be a JPG image",
)

_403_INVALID_IMAGE_TOKEN_API = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Invalid token",
)

_403_IMAGE_TOKEN_EXPIRED_API = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Token expired",
)

_404_IMAGE_FILE_NOT_FOUND_API = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="IMAGE file does not exist",
)

_404_QUESTION_NOT_FOUND_API = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Question does not exist",
)

_500_CREATE_QUESTION_FAILED_API = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail=f"Failed to save file",
)

# Exam Record API Responses
_404_EXAM_RECORD_NOT_FOUND_API = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Exam record does not exist",
)
