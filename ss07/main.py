from fastapi import FastAPI, HTTPException 
from pydantic import BaseModel 

app = FastAPI(
    title= "Manager Students"
)

student_dtb = [
    {"id": 1, "username": "Kim Ngan", "email": "kimngan@gmail.com", "password": "123"},
    {"id": 2, "username": "Ngoc", "email": "ngoc@gmail.com", "password": "456"},
    {"id": 3, "username": "Han", "email": "han@gmail.com", "password": "789"}
]

class StudentSchema(BaseModel):
    username: str
    email: str
    password: str
# Tao API them sinh vien
@app.post("/students", tags=["Students"])
def create_students(student: StudentSchema):
    student_id = len(student_dtb) + 1
    new_student = {
        "id": student_id,
        "username": student.username,
        "email": student.email,
        "password": student.password
    }
    student_dtb.append(new_student)
    return {
        "status_code": 201,
        "message": "Them thong tin thanh cong!",
        "data": new_student
    }


# Tao API lay sinh vien theo id
@app.get("/students/{student_id}", tags=["Students"])
def get_student_id(student_id:int):
    for student in student_dtb:
        if student_id == student.get("id"):
            return  {
                "status_code": 200,
                "message": "Lay danh sach thanh cong!",
                "data": student
            }
    raise HTTPException(
        status_code=404,
        detail="Khong tim thay"
    )

# Yeu cau: 
# 1: Đọc đoạn code phía dưới hiểu, phân tích
# 2: Tìm hiểu 1 số giao thức HTTP thường dùng: vd 200, 201, 500, 400
# 