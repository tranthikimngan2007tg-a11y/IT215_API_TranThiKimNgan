from datetime import datetime, timezone

from fastapi import (
    FastAPI,
    Depends,
    Query,
    Request,
    HTTPException
)

from fastapi.exceptions import RequestValidationError

from fastapi.responses import JSONResponse

from sqlalchemy.exc import IntegrityError

from sqlalchemy.orm import Session

from database import Base, engine, get_db

from models import Student

from schemas import (
    APIResponse,
    StudentCreate,
    StudentUpdate,
    StudentResponse
)

import crud


# =========================================================
# CREATE TABLE
# =========================================================

Base.metadata.create_all(bind=engine)


# =========================================================
# FASTAPI
# =========================================================

app = FastAPI(
    title="Student Management API",
    description="API quản lý sinh viên theo lớp học",
    version="1.0.0"
)


# =========================================================
# UTILITY
# =========================================================

def get_timestamp():
    return (
        datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )


def success_response(
    status_code: int,
    message: str,
    data,
    path: str
):
    return {
        "statusCode": status_code,
        "message": message,
        "data": data,
        "error": None,
        "timestamp": get_timestamp(),
        "path": path
    }


def error_response(
    status_code: int,
    message: str,
    error,
    path: str
):
    return {
        "statusCode": status_code,
        "message": message,
        "data": None,
        "error": error,
        "timestamp": get_timestamp(),
        "path": path
    }


# =========================================================
# GLOBAL EXCEPTION HANDLER
# =========================================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    return JSONResponse(
        status_code=422,
        content=error_response(
            status_code=422,
            message="Dữ liệu không hợp lệ",
            error=exc.errors(),
            path=request.url.path
        )
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exc: HTTPException
):
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            status_code=exc.status_code,
            message=str(exc.detail),
            error=exc.detail,
            path=request.url.path
        )
    )


@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception
):
    return JSONResponse(
        status_code=500,
        content=error_response(
            status_code=500,
            message="Đã xảy ra lỗi máy chủ",
            error=str(exc),
            path=request.url.path
        )
    )


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():
    return success_response(
        status_code=200,
        message="Student Management API is running",
        data={
            "docs": "/docs"
        },
        path="/"
    )


# =========================================================
# GET /students
# =========================================================

@app.get(
    "/students",
    response_model=APIResponse,
    status_code=200
)
def get_students(
    request: Request,
    search: str | None = Query(
        default=None,
        description="Tìm theo tên, mã sinh viên hoặc email"
    ),
    class_id: int | None = Query(
        default=None,
        ge=1,
        description="Lọc theo ID lớp học"
    ),
    db: Session = Depends(get_db)
):
    students = crud.get_students(
        db=db,
        search=search,
        class_id=class_id
    )

    return success_response(
        status_code=200,
        message="Lấy danh sách sinh viên thành công",
        data=students,
        path=request.url.path
    )


# =========================================================
# GET /students/{student_id}
# =========================================================

@app.get(
    "/students/{student_id}",
    response_model=APIResponse,
    status_code=200
)
def get_student(
    student_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    student = crud.get_student_by_id(
        db,
        student_id
    )

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy sinh viên"
        )

    return success_response(
        status_code=200,
        message="Lấy thông tin sinh viên thành công",
        data=student,
        path=request.url.path
    )


# =========================================================
# POST /students
# =========================================================

@app.post(
    "/students",
    response_model=APIResponse,
    status_code=201
)
def create_student(
    student_data: StudentCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    try:

        student = crud.create_student(
            db,
            student_data
        )

        return JSONResponse(
            status_code=201,
            content=success_response(
                status_code=201,
                message="Thêm sinh viên thành công",
                data=StudentResponse.model_validate(
                    student
                ).model_dump(mode="json"),
                path=request.url.path
            )
        )

    except ValueError as exc:

        db.rollback()

        return JSONResponse(
            status_code=400,
            content=error_response(
                status_code=400,
                message=str(exc),
                error=str(exc),
                path=request.url.path
            )
        )

    except IntegrityError:

        db.rollback()

        return JSONResponse(
            status_code=409,
            content=error_response(
                status_code=409,
                message="Dữ liệu bị trùng",
                error="Student code hoặc email đã tồn tại",
                path=request.url.path
            )
        )


# =========================================================
# PUT /students/{student_id}
# =========================================================

@app.put(
    "/students/{student_id}",
    response_model=APIResponse,
    status_code=200
)
def update_student(
    student_id: int,
    student_data: StudentUpdate,
    request: Request,
    db: Session = Depends(get_db)
):
    try:

        student = crud.update_student(
            db,
            student_id,
            student_data
        )

        return success_response(
            status_code=200,
            message="Cập nhật sinh viên thành công",
            data=StudentResponse.model_validate(
                student
            ),
            path=request.url.path
        )

    except LookupError as exc:

        db.rollback()

        raise HTTPException(
            status_code=404,
            detail=str(exc)
        )

    except ValueError as exc:

        db.rollback()

        return JSONResponse(
            status_code=400,
            content=error_response(
                status_code=400,
                message=str(exc),
                error=str(exc),
                path=request.url.path
            )
        )

    except IntegrityError:

        db.rollback()

        return JSONResponse(
            status_code=409,
            content=error_response(
                status_code=409,
                message="Dữ liệu bị trùng",
                error="Student code hoặc email đã tồn tại",
                path=request.url.path
            )
        )