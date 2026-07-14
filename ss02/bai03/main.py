# (1) BÁO CÁO PHÂN TÍCH
#
# - Input:
#   + Danh sách students gồm các thông tin:
#       id, name, status.

# - Output:
#   + Trả về một đối tượng JSON gồm:
#       message: Thông báo kết quả.
#       data: Danh sách sinh viên đang học.

# - Điều kiện xác định sinh viên đang học:
#   + status == "active"

# - Các bước xử lý API GET /students/active:
#   1. Client gửi request GET /students/active.
#   2. FastAPI tìm endpoint tương ứng.
#   3. Duyệt danh sách students.
#   4. Lọc các sinh viên có status == "active".
#   5. Nếu có dữ liệu:
#        - Trả về message và danh sách sinh viên.
#      Nếu không có dữ liệu:
#        - Trả về message "Không có sinh viên đang học"
#          và data là danh sách rỗng [].
#
# (2) TRIỂN KHAI
from fastapi import FastAPI
app = FastAPI()

students = [
    {"id": 1, "name": "An", "status": "active"},
    {"id": 2, "name": "Binh", "status": "inactive"},
    {"id": 3, "name": "Cuong", "status": "active"},
    {"id": 4, "name": "Dung", "status": "pending"}
]


@app.get("/students/active")
def get_active_students():
    active_students = []

    for student in students:
        if student["status"] == "active":
            active_students.append(student)

    if len(active_students) == 0:
        return {
            "message": "Không có sinh viên đang học",
            "data": []
        }

    return {
        "message": "Danh sách sinh viên đang học",
        "data": active_students
    }