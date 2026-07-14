from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

app = FastAPI(title="Elearning Course API", version="1.0.1")

courses_db = [
    {"id": 1, "course_name": "FastAPI Masterclass", "duration_hours": 32, "price": 1500000, "status": "active", "created_at": "2026-07-01T02:00:00Z"},
    {"id": 2, "course_name": "NextJS Next-Level", "duration_hours": 45, "price": 1800000, "status": "active", "created_at": "2026-07-01T03:15:00Z"}
]

class CourseCreate(BaseModel):
    course_name: str = Field(..., min_length=5, description="Tên khóa học phải có ít nhất 5 ký tự")
    duration_hours: int = Field(..., gt=0, description="Thời lượng phải lớn hơn 0")
    price: int = Field(..., ge=0, description="Học phí phải lớn hơn hoặc bằng 0")

class CourseResponse(BaseModel):
    id: int
    course_name: str
    duration_hours: int
    price: int
    status: str
    created_at: str

class StandardResponse(BaseModel):
    statusCode: int
    message: str
    data: Optional[dict | list] = None
    error: Optional[str] = None
    timestamp: str
    path: str

def create_response(status_code: int, message: str, data=None, error=None, path: str = ""):
    return {
        "statusCode": status_code,
        "message": message,
        "data": data,
        "error": error,
        "timestamp": datetime.now().isoformat() + "Z",
        "path": path
    }

@app.get("/courses", response_model=StandardResponse)
async def get_all_courses(request: Request):
    return create_response(
        status_code=200,
        message="Lấy danh sách khóa học thành công!",
        data=courses_db,
        path=str(request.url.path)
    )

@app.post("/courses", status_code=201, response_model=StandardResponse)
async def create_course(course: CourseCreate, request: Request):
    # Kiểm tra trùng tên khóa học
    for existing in courses_db:
        if existing["course_name"].lower() == course.course_name.lower():
            raise HTTPException(
                status_code=400,
                detail=create_response(
                    status_code=400,
                    message="Lỗi: Tên khóa học này đã tồn tại trong danh mục đào tạo!",
                    data=None,
                    error="ERR-EDU-01: Course name duplicates an existing record in memory array.",
                    path=str(request.url.path)
                )
            )

    new_id = max([c["id"] for c in courses_db]) + 1 if courses_db else 1
    new_course = {
        "id": new_id,
        "course_name": course.course_name,
        "duration_hours": course.duration_hours,
        "price": course.price,
        "status": "active",
        "created_at": datetime.utcnow().isoformat() + "Z"
    }
    courses_db.append(new_course)

    return create_response(
        status_code=201,
        message="Tạo mới khóa học thành công!",
        data=new_course,
        path=str(request.url.path)
    )

@app.delete("/courses/{course_id}", response_model=StandardResponse)
async def delete_course(course_id: int, request: Request):
    for index, course in enumerate(courses_db):
        if course["id"] == course_id:
            courses_db.pop(index)
            return create_response(
                status_code=200,
                message="Xóa khóa học thành công!",
                data=None,
                path=str(request.url.path)
            )

    raise HTTPException(
        status_code=404,
        detail=create_response(
            status_code=404,
            message="Lỗi: Không tìm thấy mã khóa học yêu cầu để xóa!",
            data=None,
            error="ERR-EDU-02: Target course ID can not be found.",
            path=str(request.url.path)
        )
    )


