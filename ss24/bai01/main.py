from typing import Callable, Iterable

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(
    title="MegaMart ERP - RBAC & CORS",
    version="1.0.0",
)


ALLOWED_ORIGINS = ["https://internal.megamart.com"]
ALLOWED_METHODS = ["GET", "POST"]
ALLOWED_HEADERS = ["Content-Type", "X-User-Role"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=ALLOWED_METHODS,
    allow_headers=ALLOWED_HEADERS,
)

ROLES = {"ADMIN", "HR", "STAFF"}

ROLE_RULES = {
    "/api/v1/salary/modify": {"ADMIN", "HR"},
    "/api/v1/system/settings": {"ADMIN"},
    "/api/v1/profile": {"ADMIN", "HR", "STAFF"},
}

@app.middleware("http")
async def rbac_middleware(request: Request, call_next: Callable):
    # Luôn thêm header hệ thống vào response cuối cùng
    # Header này không dùng để xác thực quyền
    if request.method == "OPTIONS":
        # CORS preflight phải được để CORSMiddleware xử lý
        # Không chặn OPTIONS bằng RBAC
        return await call_next(request)

    required_roles = ROLE_RULES.get(request.url.path)

    # Route không nằm trong ROLE_RULES => không yêu cầu RBAC ở middleware này
    if required_roles is None:
        response = await call_next(request)
        response.headers["X-System-Name"] = "MegaMart ERP"
        return response

    user_role = request.headers.get("X-User-Role", "").strip().upper()

    # Không có role hoặc role không hợp lệ => 403
    if user_role not in ROLES or user_role not in required_roles:
        return JSONResponse(
            status_code=403,
            content={"error": "Permission Denied"},
            headers={"X-System-Name": "MegaMart ERP"},
        )

    response = await call_next(request)
    response.headers["X-System-Name"] = "MegaMart ERP"
    return response


@app.get("/api/v1/salary/modify")
async def modify_salary():
    return {
        "message": "Salary API accessed",
        "allowed_roles": ["ADMIN", "HR"],
    }


@app.get("/api/v1/system/settings")
async def system_settings():
    return {
        "message": "System settings accessed",
        "allowed_roles": ["ADMIN"],
    }


@app.get("/api/v1/profile")
async def profile():
    return {
        "message": "Profile API accessed",
        "allowed_roles": ["ADMIN", "HR", "STAFF"],
    }


# Endpoint công khai để kiểm tra hệ thống / CORS
@app.get("/health")
async def health():
    return {"status": "UP"}
