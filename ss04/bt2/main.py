from fastapi import FastAPI

app = FastAPI()

# ==========================
# DỮ LIỆU ĐƠN HÀNG
# ==========================

orders = [
    {"id": 1, "customer_name": "Nguyễn Văn An", "total": 250000, "status": "pending"},
    {"id": 2, "customer_name": "Trần Thị Bình", "total": 500000, "status": "paid"},
    {"id": 3, "customer_name": "Lê Văn Cường", "total": 150000, "status": "cancelled"},
    {"id": 4, "customer_name": "Phạm Thị Dung", "total": 320000, "status": "pending"}
]

# ==================================================
# PHẦN 1. PHÂN TÍCH LỖI
# ==================================================

# Câu 1:
# Endpoint hiện tại có Path Parameter không?
#
# Có.
# Endpoint được khai báo:
#
# @app.get("/orders/status/{status}")
#
# Trong đó status là Path Parameter.


# Câu 2:
# Path Parameter trong bài này là gì?
#
# Path Parameter là:
#
# status
#
# Giá trị của status sẽ được lấy trực tiếp từ URL.


# Câu 3:
# Khi gọi:
#
# GET /orders/status/pending
#
# thì biến status sẽ nhận giá trị:
#
# "pending"


# Câu 4:
# Vì sao API hiện tại trả về sai dữ liệu?
#
# Vì API không sử dụng biến status để lọc dữ liệu.
# Thay vào đó API trả về toàn bộ danh sách orders.


# Câu 5:
# Dòng code khiến API bỏ qua giá trị status là:
#
# return orders
#
# Vì dòng lệnh này trả về toàn bộ danh sách đơn hàng
# mà không kiểm tra trạng thái.


# ==================================================
# PHẦN 2. SỬA CODE THEO YÊU CẦU
# ==================================================

# Khai báo Path Parameter để nhận trạng thái từ URL.
# Tên biến trong {} phải trùng với tên tham số của hàm.

@app.get("/orders/status/{status}")
def get_orders_by_status(status: str):

    # Danh sách trạng thái hợp lệ
    valid_status = ["pending", "paid", "cancelled"]

    # Kiểm tra trạng thái có hợp lệ hay không
    if status not in valid_status:
        return {
            "message": "Trạng thái đơn hàng không hợp lệ"
        }

    # Tạo danh sách chứa các đơn hàng có trạng thái trùng với status
    result = []

    # Duyệt toàn bộ danh sách đơn hàng
    for order in orders:

        # Nếu trạng thái đơn hàng trùng với status thì thêm vào kết quả
        if order["status"] == status:
            result.append(order)

    # Trả về danh sách sau khi lọc
    return result


# ==================================================
# PHẦN 3. TEST CASE
# ==================================================

# Test 1
#
# URL:
# GET /orders/status/pending
#
# Kết quả mong muốn:
#
# [
#     {
#         "id": 1,
#         "customer_name": "Nguyễn Văn An",
#         "total": 250000,
#         "status": "pending"
#     },
#     {
#         "id": 4,
#         "customer_name": "Phạm Thị Dung",
#         "total": 320000,
#         "status": "pending"
#     }
# ]


# Test 2
#
# URL:
# GET /orders/status/paid
#
# Kết quả mong muốn:
#
# [
#     {
#         "id": 2,
#         "customer_name": "Trần Thị Bình",
#         "total": 500000,
#         "status": "paid"
#     }
# ]


# Test 3
#
# URL:
# GET /orders/status/shipping
#
# Kết quả mong muốn:
#
# {
#     "message": "Trạng thái đơn hàng không hợp lệ"
# }


# ==================================================
# PHẦN 4. KẾT LUẬN
# ==================================================

# - Path Parameter dùng để nhận dữ liệu trực tiếp từ URL.
#
# - Trong bài này, Path Parameter là status.
#
# - Giá trị status được truyền từ URL vào hàm để xử lý.
#
# - API phải sử dụng giá trị status để lọc đúng dữ liệu.
#
# - Nếu bỏ qua Path Parameter thì API vẫn chạy được nhưng
#   sẽ trả về sai nghiệp vụ.
#
# - Cần kiểm tra trạng thái hợp lệ trước khi xử lý.
#
# - Nếu trạng thái không hợp lệ thì trả về thông báo lỗi.
#
# - Nếu trạng thái hợp lệ thì chỉ trả về các đơn hàng có
#   trạng thái trùng với status.