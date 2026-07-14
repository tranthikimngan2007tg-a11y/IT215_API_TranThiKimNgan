from fastapi import FastAPI, Request, status, Response
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.exc import IntegrityError
import uvicorn
import time
from collections import defaultdict
from datetime import datetime

from app.core.config import settings
from app.core.database import Base, engine
from app.api.v1.api import api_router

# Nhập các Database Models để đảm bảo chúng được khai báo trong Base trước khi tạo bảng
from app.models.user import User
from app.models.class_room import ClassRoom
from app.models.student import Student
from app.models.score import Score

# Tự động tạo tất cả các bảng nếu chưa tồn tại
Base.metadata.create_all(bind=engine)

# Middleware giới hạn tần suất yêu cầu (Rate Limiting) bằng bộ nhớ đệm trong RAM
class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit: int = 100, window: int = 60):
        super().__init__(app)
        self.limit = limit
        self.window = window
        self.requests = defaultdict(list)

    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path
        # Không áp dụng rate limit cho các tài liệu API docs để tránh làm gián đoạn thử nghiệm
        if path.startswith("/docs") or path.startswith("/openapi.json") or path.startswith("/redoc") or path == "/":
            return await call_next(request)
            
        client_ip = request.client.host if request.client else "127.0.0.1"
        now = time.time()
        
        # Loại bỏ các thời điểm gửi yêu cầu cũ hơn khoảng thời gian (window) giới hạn
        self.requests[client_ip] = [t for t in self.requests[client_ip] if now - t < self.window]
        
        if len(self.requests[client_ip]) >= self.limit:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "statusCode": status.HTTP_429_TOO_MANY_REQUESTS,
                    "message": "Yêu cầu quá nhiều lần. Vui lòng thử lại sau ít phút.",
                    "data": None,
                    "error": "Too Many Requests",
                    "timestamp": datetime.now().isoformat()
                }
            )
            
        self.requests[client_ip].append(now)
        return await call_next(request)

# Middleware bảo mật các Header phản hồi (HTTP Security Headers)
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Hệ thống API quản lý sinh viên chuyên nghiệp sử dụng FastAPI, MySQL/SQLite và SQLAlchemy ORM. Hỗ trợ phân quyền RBAC (Giảng viên / Sinh viên), xác thực bảo mật bằng JWT và tìm kiếm nâng cao tối ưu hóa hiệu năng bằng SQL Index.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    swagger_ui_parameters={"persistAuthorization": True},
)

# Đăng ký các Middleware bảo mật
app.add_middleware(RateLimitMiddleware, limit=100, window=60)
app.add_middleware(SecurityHeadersMiddleware)

# Cấu hình CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FIELD_MAPPING = {
    "username": "Tên đăng nhập",
    "email": "Email",
    "password": "Mật khẩu",
    "student_code": "Mã sinh viên",
    "first_name": "Họ và tên đệm",
    "last_name": "Tên sinh viên",
    "date_of_birth": "Ngày sinh",
    "gender": "Giới tính",
    "phone": "Số điện thoại",
    "class_id": "Lớp học",
    "subject_name": "Tên môn học",
    "score_value": "Điểm số",
    "weight": "Trọng số",
    "remarks": "Nhận xét",
}

def translate_pydantic_error(err: dict) -> str:
    err_type = err.get("type", "")
    err_ctx = err.get("ctx", {})
    msg = err.get("msg", "")
    loc = err.get("loc", [])
    
    # Lấy tên trường bị lỗi
    field_name = str(loc[-1]) if loc else ""
    friendly_field = FIELD_MAPPING.get(field_name, field_name)
    
    # Loại bỏ tiền tố "Value error, " do Pydantic sinh ra từ ValueError
    if msg.startswith("Value error, "):
        msg = msg.replace("Value error, ", "")

    # Dịch thông báo lỗi tự nhiên
    if err_type == "missing" or (err_type == "string_too_short" and err.get("input") == ""):
        if friendly_field:
            return f"{friendly_field} không được để trống."
        return "Trường thông tin này là bắt buộc và không được để trống."
        
    if err_type == "int_parsing":
        return f"{friendly_field} phải là số nguyên hợp lệ."
    elif err_type == "float_parsing":
        return f"{friendly_field} phải là số thực hợp lệ."
    elif err_type in ("date_parsing", "date_from_datetime_parsing"):
        return f"{friendly_field} không đúng định dạng ngày (YYYY-MM-DD)."
    elif err_type == "string_too_short":
        min_len = err_ctx.get("min_length", "")
        return f"{friendly_field} phải có độ dài tối thiểu là {min_len} ký tự."
    elif err_type == "string_too_long":
        max_len = err_ctx.get("max_length", "")
        return f"{friendly_field} có độ dài tối đa không quá {max_len} ký tự."
    elif err_type == "greater_than_equal":
        ge = err_ctx.get("ge", "")
        return f"{friendly_field} phải lớn hơn hoặc bằng {ge}."
    elif err_type == "less_than_equal":
        le = err_ctx.get("le", "")
        return f"{friendly_field} phải nhỏ hơn hoặc bằng {le}."
    elif err_type == "greater_than":
        gt = err_ctx.get("gt", "")
        return f"{friendly_field} phải lớn hơn {gt}."
    elif err_type == "less_than":
        lt = err_ctx.get("lt", "")
        return f"{friendly_field} phải nhỏ hơn {lt}."
    elif err_type == "string_pattern_mismatch":
        pattern = err_ctx.get("pattern", "")
        if "Male|Female|Other" in pattern:
            return f"{friendly_field} chỉ chấp nhận các giá trị: 'Male', 'Female' hoặc 'Other'."
        elif "a-zA-Z0-9_-" in pattern or "a-zA-Z0-9_-" in pattern:
            return f"{friendly_field} không hợp lệ (chỉ chấp nhận chữ cái không dấu, số, dấu gạch dưới '_' hoặc gạch ngang '-')."
        elif "A-Z0-9_-" in pattern:
            return f"{friendly_field} không hợp lệ (chỉ chấp nhận chữ cái viết hoa không dấu, số, dấu gạch dưới '_' hoặc gạch ngang '-')."
        return f"{friendly_field} không đúng định dạng yêu cầu."
    elif err_type == "enum":
        expected = err_ctx.get("expected", "")
        return f"{friendly_field} không hợp lệ (chỉ chấp nhận các giá trị: {expected})."
    elif err_type == "value_error" and "email" in msg.lower():
        return "Địa chỉ email không đúng định dạng."
    elif "value_error" in err_type or err_type == "value_error":
        if msg and not msg.endswith("."):
            return msg + "."
        return msg
        
    if msg and not msg.endswith("."):
        return msg + "."
    return msg

# Exception Handler cho các lỗi HTTP (như 400, 401, 403, 404,...)
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "statusCode": exc.status_code,
            "message": exc.detail,
            "data": None,
            "error": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )

# Exception Handler cho lỗi validate dữ liệu đầu vào (Pydantic Validation Errors)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    # Dịch danh sách lỗi sang tiếng Việt thân thiện
    friendly_errors = []
    for err in errors:
        translated_msg = translate_pydantic_error(err)
        friendly_errors.append(translated_msg)
    
    # Lấy lỗi đầu tiên làm thông báo chính theo yêu cầu của user
    error_message = friendly_errors[0] if friendly_errors else "Dữ liệu yêu cầu gửi lên không hợp lệ."
    
    # Loại bỏ các đối tượng không thể chuyển đổi sang JSON (như các đối tượng Exception trong ctx)
    sanitized_errors = []
    for err in errors:
        err_copy = dict(err)
        if "ctx" in err_copy:
            ctx_copy = {}
            for k, v in err_copy["ctx"].items():
                if isinstance(v, Exception):
                    ctx_copy[k] = str(v)
                else:
                    ctx_copy[k] = v
            err_copy["ctx"] = ctx_copy
        sanitized_errors.append(err_copy)

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,  # Trả về mã 400 cho client
        content={
            "statusCode": status.HTTP_400_BAD_REQUEST,
            "message": error_message,
            "data": None,
            "error": friendly_errors,  # Trả về danh sách chi tiết các lỗi tiếng Việt thân thiện
            "timestamp": datetime.now().isoformat()
        }
    )

# Exception Handler cho các lỗi vi phạm ràng buộc cơ sở dữ liệu (Khóa ngoại, Trùng lặp dữ liệu)
@app.exception_handler(IntegrityError)
async def integrity_exception_handler(request: Request, exc: IntegrityError):
    err_msg = str(exc.orig)
    message = "Lỗi vi phạm tính toàn vẹn dữ liệu trong cơ sở dữ liệu."
    
    # Phân tích thông tin lỗi để hiển thị tiếng Việt rõ nghĩa
    if "foreign key constraint fails" in err_msg.lower():
        if "`class_id`" in err_msg or "references `classes`" in err_msg.lower():
            message = "Không tìm thấy thông tin lớp học liên kết."
        elif "`user_id`" in err_msg or "references `users`" in err_msg.lower():
            message = "Không tìm thấy tài khoản người dùng liên kết."
        elif "`student_id`" in err_msg or "references `students`" in err_msg.lower():
            message = "Không tìm thấy hồ sơ sinh viên liên kết."
        else:
            message = "Không tìm thấy thông tin liên kết dữ liệu hợp lệ (Lỗi khóa ngoại)."
    elif "duplicate entry" in err_msg.lower() or "1062" in err_msg:
        message = "Dữ liệu bị trùng lặp. Vui lòng kiểm tra lại thông tin duy nhất (Mã hoặc Email)."

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "statusCode": status.HTTP_400_BAD_REQUEST,
            "message": message,
            "data": None,
            "error": err_msg,
            "timestamp": datetime.now().isoformat()
        }
    )

# Exception Handler cho các lỗi Server nội bộ chưa được bắt (500 Internal Server Error)
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": "Đã xảy ra lỗi hệ thống nội bộ.",
            "data": None,
            "error": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )

# Điều hướng trang chủ mặc định sang trang tài liệu Swagger UI
@app.get("/", include_in_schema=False)
def root_redirect():
    return RedirectResponse(url="/docs")

# Đăng ký các nhóm API chính
app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
