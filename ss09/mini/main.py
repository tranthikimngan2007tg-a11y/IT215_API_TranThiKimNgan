from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import re

app = FastAPI(
    title="Team Task Management API",
    description="API quản lý công việc nhóm",
    version="1.0"
)

# ==========================
# DATABASE GIẢ
# ==========================

tasks_db = [
    {
        "id": 1,
        "title": "Thiết kế Database",
        "description": "Thiết kế CSDL cho dự án",
        "assignee": "Ngân",
        "priority": 1,
        "status": "todo",
        "created_at": datetime.now().isoformat(),
        "internal_notes": "Admin only"
    },
    {
        "id": 2,
        "title": "Thiết kế API",
        "description": "Viết các API chính",
        "assignee": "An",
        "priority": 2,
        "status": "in_progress",
        "created_at": datetime.now().isoformat(),
        "internal_notes": "Không hiển thị"
    }
]

# ==========================
# SCHEMA
# ==========================

class TaskCreateSchema(BaseModel):
    title: str = Field(..., min_length=3, max_length=150)
    description: str
    assignee: str = Field(..., min_length=2)
    priority: int = Field(..., ge=1, le=5)


class TaskUpdateSchema(BaseModel):
    title: str = Field(..., min_length=3, max_length=150)
    description: str
    assignee: str = Field(..., min_length=2)
    priority: int = Field(..., ge=1, le=5)
    status: str


class TaskPublicResponse(BaseModel):
    id: int
    title: str
    description: str
    assignee: str
    priority: int
    status: str
    created_at: str


# ==========================
# RESPONSE CHUNG
# ==========================

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
        "timestamp": datetime.now().isoformat(),
        "path": path
    }


def error_response(
    status_code: int,
    message: str,
    error: str,
    path: str
):
    return {
        "statusCode": status_code,
        "message": message,
        "data": None,
        "error": error,
        "timestamp": datetime.now().isoformat(),
        "path": path
    }


# ==========================
# GLOBAL EXCEPTION HANDLER
# ==========================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):

    if isinstance(exc.detail, dict):
        detail = exc.detail
    else:
        detail = {
            "message": str(exc.detail),
            "error": str(exc.detail)
        }

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            exc.status_code,
            detail["message"],
            detail["error"],
            request.url.path
        )
    )


# ==========================
# HÀM HỖ TRỢ
# ==========================

def find_task(task_id: int):

    for task in tasks_db:
        if task["id"] == task_id:
            return task

    return None


# ==========================
# CREATE TASK
# POST /tasks
# ==========================

@app.post("/tasks")
def create_task(task: TaskCreateSchema):

    # Kiểm tra title bị trùng

    for item in tasks_db:
        if item["title"].lower() == task.title.lower():

            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Lỗi: Tiêu đề công việc này đã tồn tại trong nhóm!",
                    "error": "ERR-TASK-01: Task conflict"
                }
            )

    # Sinh ID

    new_id = 1

    if len(tasks_db) > 0:
        new_id = max(x["id"] for x in tasks_db) + 1

    new_task = {
        "id": new_id,
        "title": task.title,
        "description": task.description,
        "assignee": task.assignee,
        "priority": task.priority,
        "status": "todo",
        "created_at": datetime.now().isoformat(),
        "internal_notes": "Admin only"
    }

    tasks_db.append(new_task)

    public_data = {
        "id": new_task["id"],
        "title": new_task["title"],
        "description": new_task["description"],
        "assignee": new_task["assignee"],
        "priority": new_task["priority"],
        "status": new_task["status"],
        "created_at": new_task["created_at"]
    }

    return success_response(
        201,
        "Tạo mới công việc nhóm thành công!",
        public_data,
        "/tasks"
    )


# ==========================
# GET TASK BY ID
# ==========================

@app.get("/tasks/{task_id}")
def get_task(task_id: int):

    task = find_task(task_id)

    if task is None:

        raise HTTPException(
            status_code=404,
            detail={
                "message": "Lỗi: Không tìm thấy ID công việc yêu cầu trong hệ thống!",
                "error": "ERR-TASK-04: Resource not found"
            }
        )

    public_data = {
        "id": task["id"],
        "title": task["title"],
        "description": task["description"],
        "assignee": task["assignee"],
        "priority": task["priority"],
        "status": task["status"],
        "created_at": task["created_at"]
    }

    return success_response(
        200,
        "Lấy thông tin công việc thành công!",
        public_data,
        f"/tasks/{task_id}"
    )