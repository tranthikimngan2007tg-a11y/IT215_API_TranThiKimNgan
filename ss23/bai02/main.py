from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer

app = FastAPI(title="Learning Management System - Security Practice")

# Chỉ cho phép 2 frontend được quy định.
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

TOKENS = {
    "admin-token": {
        "username": "admin01",
        "role": "admin",
        "is_active": True,
    },
    "user-token": {
        "username": "student01",
        "role": "user",
        "is_active": True,
    },
    "locked-token": {
        "username": "locked01",
        "role": "user",
        "is_active": False,
    },
}


@app.middleware("http")
async def authentication_middleware(request: Request, call_next):
    # /health công khai.
    # OPTIONS phải được CORS middleware xử lý, không yêu cầu JWT.
    if request.url.path == "/health" or request.method == "OPTIONS":
        response = await call_next(request)
        response.headers["X-System-Name"] = "Learning Management System"
        return response

    if "authorization" not in request.headers:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Authorization header is required"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    response = await call_next(request)
    response.headers["X-System-Name"] = "Learning Management System"
    return response


def get_current_user(token: str = Depends(oauth2_scheme)):
    user = TOKENS.get(token)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    return user


def require_admin(current_user: dict = Depends(get_current_user)):
    # Chỉ role=admin mới có quyền xóa khóa học.
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin permission required",
        )

    return current_user


@app.get("/health")
def health_check():
    return {"status": "UP"}


@app.get("/courses")
def get_courses(current_user: dict = Depends(get_current_user)):
    return {
        "items": [
            {"id": 1, "name": "FastAPI Basic"},
            {"id": 2, "name": "FastAPI Security"},
        ],
        "requested_by": current_user["username"],
    }


@app.delete("/admin/courses/{course_id}")
def delete_course(
    course_id: int,
    current_user: dict = Depends(require_admin),
):
    return {
        "message": f"Course {course_id} has been deleted",
        "deleted_by": current_user["username"],
    }
