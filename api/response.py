from fastapi import HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")


# Render Page Responses
# def render_index_page(request, **context):
#     ctx = {"request": request, **context}
#     return templates.TemplateResponse("index.html", ctx)


# 3xx Responses
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

# 4xx Responses
_401_LOGIN_FAILED = HTMLResponse(
    "登入失敗",
    status_code=status.HTTP_401_UNAUTHORIZED,
)

_403_CANNOT_ACCESS_OTHER_USER_DATA = HTMLResponse(
    "您無法存取其他使用者的資料",
    status_code=status.HTTP_403_FORBIDDEN,
)

_403_NOT_A_STUDENT = HTMLResponse(
    "您的角色非學生，無法使用該功能",
    status_code=status.HTTP_403_FORBIDDEN,
)

_403_NOT_A_ADMIN_OR_TEACHER = HTMLResponse(
    "您的角色非管理員或教師，無法使用該功能",
    status_code=status.HTTP_403_FORBIDDEN,
)

_404_EXAM_TYPE_NOT_FOUND = HTMLResponse(
    "該考試科目不存在",
    status_code=status.HTTP_404_NOT_FOUND,
)

_404_EXAM_RECORD_NOT_FOUND = HTMLResponse(
    "該測驗紀錄不存在",
    status_code=status.HTTP_404_NOT_FOUND,
)

# Question API Responses
_403_NOT_LOGIN_API = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Not logged in",
)

_403_INVALID_IMAGE_TOKEN_API = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Invalid token",
)

_403_IMAGE_TOKEN_EXPIRED_API = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Token expired",
)

_404_QUESTION_NOT_FOUND_API = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Question does not exist",
)

_404_IMAGE_FILE_NOT_FOUND_API = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="IMAGE file does not exist",
)


# tmp
_409_USER_EXISTS_API = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="User already exists",
)
