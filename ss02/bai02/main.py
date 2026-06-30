# (1) PHÂN TÍCH LỖI

# - Endpoint hiện tại trong source code:
#       GET /student

# - Vì sao gọi GET /students bị lỗi 404 Not Found?
#   + Vì trong chương trình không tồn tại endpoint "/students".
#   + FastAPI chỉ khai báo endpoint "/student".
#   + Khi frontend gọi "/students", FastAPI không tìm thấy route
#     nên trả về lỗi 404 Not Found.

# - Vì sao endpoint "/student" chưa phù hợp?
#   + "student" là số ít (một sinh viên).
#   + API này có nhiệm vụ trả về danh sách nhiều sinh viên.
#   + Theo chuẩn RESTful nên sử dụng "/students".

# - Vì sao "return students[0]" chưa đúng?
#   + students[0] chỉ lấy phần tử đầu tiên của danh sách.
#   + Khách hàng yêu cầu trả về toàn bộ danh sách sinh viên.
#   + Vì vậy phải trả về biến students.

# - API đúng theo yêu cầu khách hàng:
#       GET /students

# (2) SỬA LỖI
from fastapi import FastAPI
app = FastAPI()

students = [
    {"id": 1, "name": "An"},
    {"id": 2, "name": "Binh"},
    {"id": 3, "name": "Cuong"}
]

@app.get("/students")
def get_students():
    return students