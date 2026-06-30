# BÀI 1: SỬA LỖI LEGACY CODE FASTAPI
#
# (1) PHÂN TÍCH LỖI
#
# - Endpoint cũ:
#       GET /getStudents

# - Trace luồng xử lý:
#   1. Client gửi request GET /getStudents.
#   2. FastAPI tìm route @app.get("/getStudents").
#   3. Hàm get_students() được thực thi.
#   4. Hàm trả về:
#          "Danh sach sinh vien: " + str(students)
#   5. FastAPI gửi dữ liệu về dưới dạng String.

# - Vì sao không nên trả về String?
#   + str(students) biến List thành chuỗi.
#   + Frontend mong nhận JSON Array để có thể xử lý dữ liệu.
#   + Khi nhận String, Frontend không thể dùng map(), forEach()...

# - Lỗi REST Endpoint:
#   + /getStudents không đúng chuẩn RESTful.
#   + HTTP Method (GET) đã thể hiện hành động.
#   + Endpoint chỉ nên biểu diễn tài nguyên.
#   + Endpoint đúng là:
#           GET /students

# (2) SỬA LỖI
from fastapi import FastAPI

app = FastAPI()

students = [
    "An",
    "Binh",
    "Cuong"
]

@app.get("/students")
def get_students():
    return students