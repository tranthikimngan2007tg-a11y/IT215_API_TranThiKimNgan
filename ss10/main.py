# mock data là gì?
# là dữ liệu giả định được tạo ra để mô phỏng dữ liệu thật để kiểm thử trong quá trình phát triển
# dữ liệu phải được lưu ở Database -> mySql(hệ quản trị cơ sở dữ liệu) -> sql
# ngôn ngữ lập trình python
# sql và ngôn ngữ pyhton cần có thông dịch viên để giao tiếp ORM
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db, Base, engine
from model import StudentRequestDTO, StudentModel
from student_services import create_student

app = FastAPI(title="Demo FastApi")

Base.metadata.create_all(bind=engine)


@app.get("/test-connections")
def test_connections(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"message": "Kết nối thành công!"}
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Lỗi không kết nối được: {str(e)}"
        )


@app.post("/students", tags=["Students"])
def add_students(
    student: StudentRequestDTO,
    db: Session = Depends(get_db)
):
    return create_student(db, student)