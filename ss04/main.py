from fastapi import FastAPI
#Kiểm soát và xử lí dữ liệu đầu vào của người dùng
from pydantic import BaseModel, HTTPException

app = FastAPI(
    title = "Manager Student",
    description = "Đây là API quản li sinh viên Rikkei",
    version = "1.0.1"
)
#Định nghĩa dữ liệu người dùng
class StudentSchema(BaseModel):
    username : str
    password : str
    age: int
    status: bool = True

#Tạo Mock Data (Dữ liệu mẫu)
student_dtb = [
    {"id":1, "username": "minhnghia", "password":"123", "age": 18},
    {"id":2, "username": "nhathuy", "password":"456", "age": 35, "status": False},
    {"id":1, "username": "minhduc", "password":"123", "age": 18},
    {"id":1, "username": "minhnghia", "password":"123", "age": 28},
]

#Tạo API để lấy danh sach sinh viên
#decorator
@app.get("/studens", tags =["Student"])
def get_all_studens():
    return {
        #Mã trạng thái: 200 - 300 tương đương xử lí thànhc ông
        "status_code": 200,
        "message": "Lấy danh sách thành công",
        "data": student_dtb
    }
# Tạo API để thêm sinh viên
@app.post("/students", tags=["Students"])
def add_students(student: StudentSchema):
    student_id = len(student_dtb) + 1
    new_student = {
        "id": student_id,
        "username": student.username,
        "passwword": student.password
    }
    student_dtb.append(new_student)
    return {
        "status_code": 201,
        "message": "Thêm sinh viên thành công",
        "data": new_student
    }

# Tạo API để lấy 1 sinh viên cụ thể
#Path parameter
@app.get("/students/{student_id}")
def get_student(student_id: int):
    for student in student_dtb:
        if student_id == student.get("id"):
            return {
                "status_code": 200,
                "message": "Lấy sinh viên thành công",
                "data": student
            }
        return {
            "message": "Không tìm thấy"
        }
#Lấy danh sach sinh viên nhưng lọc theo điều kiện
#Query parameter

@app.get("/students", tags=["Students"], summary="lấy ds sinh vien theo điều kiện")
def get_students(
    keyword: str,
    limit: int,
    #status: bool

):
    list_student =[]
    for student in student_dtb:
        if keyword.lowed() in student.get("username"):
            list_student.append(student)
    if not list_student:
        return {
            "message": "Không tìm thấy"
        }
    result = list_student[:limit]
    return {
        "status_code": 200,
        "message": "Lấy danh sách thành công",
        "data": list_student
    }

# tạo api để xóa 1 sinh viên theo ID
@app.delete("/students/{student_id}", tags=["Delete"])
def delete_student(student_id: int):
    for student in student_dtb:
        if student.get("id") == student_id:
            student_dtb.remove(student)
            return {
                "status_code": 200,
                "message": "Xóa sinh viên có id thành công"
            }
    raise HTTPException(
        status_code=404,
        detail="Không tìm thấy sinh viên"
        )

# API cập nhật sinh viên theo ID
@app.put("/students/{student_id}", tags=["Update"])
def update_student(student_id: int, student: StudentSchema):
    for s in student_dtb:
        if s.get("id") == student_id:
            s.get("username") = student.username
            s.get("password") = student.password
            s.get("age") = student.age
            s["status"] = student.status
            return {
                "status_code": 200,
                "message": f"Cập nhật sinh viên có id {student_id} thành công",
                "data": s
            }
    raise HTTPException(status_code=404, detail="Không tìm thấy sinh viên")