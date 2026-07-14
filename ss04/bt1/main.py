from fastapi import FastAPI, HTTPException

app = FastAPI()

# ==========================
# DỮ LIỆU SẢN PHẨM
# ==========================

products = [
    {"id": 1, "name": "Laptop Dell", "price": 15000000},
    {"id": 2, "name": "Chuột Logitech", "price": 350000},
    {"id": 3, "name": "Bàn phím cơ", "price": 1200000}
]

# ==================================================
# PHẦN 1. PHÂN TÍCH LỖI
# ==================================================

# Câu 1:
# Khi gọi GET /products/1, API trả về 404 Not Found vì endpoint được khai báo là:
#
# @app.get("/products/product_id")
#
# FastAPI hiểu "/products/product_id" là một đường dẫn cố định (Static Path),
# chỉ chấp nhận URL:
#
# GET /products/product_id
#
# Khi gọi:
#
# GET /products/1
#
# sẽ không có endpoint nào khớp nên FastAPI trả về lỗi 404 Not Found.


# Câu 2:
# Dòng code khai báo sai Path Parameter là:
#
# @app.get("/products/product_id")


# Câu 3:
# "/products/product_id" không phải là Path Parameter vì product_id
# không được đặt trong dấu ngoặc nhọn {}.
#
# Sai:
#
# "/products/product_id"
#
# Đúng:
#
# "/products/{product_id}"


# Câu 4:
# Endpoint đúng cần sửa là:
#
# @app.get("/products/{product_id}")


# ==================================================
# PHẦN 2. SỬA CODE THEO YÊU CẦU
# ==================================================

# Khai báo Path Parameter bằng dấu {} để nhận product_id từ URL.
# Tên biến trong {} phải trùng với tên tham số của hàm.
# Ở đây đều là product_id nên FastAPI sẽ tự động truyền giá trị từ URL vào hàm.

@app.get("/products/{product_id}")
def get_product_detail(product_id: int):

    # Duyệt danh sách sản phẩm
    for product in products:

        # Nếu id của sản phẩm trùng với product_id thì trả về sản phẩm
        if product["id"] == product_id:
            return product

    # Nếu không tìm thấy sản phẩm thì trả về lỗi 404
    raise HTTPException(
        status_code=404,
        detail="Không tìm thấy sản phẩm"
    )


# ==================================================
# PHẦN 3. TEST CASE
# ==================================================

# Test 1
#
# URL:
# GET /products/1
#
# Kết quả mong muốn:
#
# {
#     "id": 1,
#     "name": "Laptop Dell",
#     "price": 15000000
# }


# Test 2
#
# URL:
# GET /products/2
#
# Kết quả mong muốn:
#
# {
#     "id": 2,
#     "name": "Chuột Logitech",
#     "price": 350000
# }


# Test 3
#
# URL:
# GET /products/10
#
# Kết quả mong muốn:
#
# Status Code: 404
#
# {
#     "detail": "Không tìm thấy sản phẩm"
# }


# Test 4
#
# URL:
# GET /products/abc
#
# Kết quả mong muốn:
#
# FastAPI tự động báo lỗi validate vì product_id được khai báo là kiểu int.
# Chuỗi "abc" không thể chuyển thành số nguyên.


# ==================================================
# PHẦN 4. KẾT LUẬN
# ==================================================

# - Path Parameter là tham số được truyền trực tiếp trên URL để xác định
#   một tài nguyên cụ thể (ví dụ: sản phẩm theo id).
#
# - Trong FastAPI, Path Parameter được khai báo bằng dấu {}.
#
# - Giá trị trên URL sẽ được truyền vào tham số của hàm.
#
# - Tên biến trong {} phải trùng với tên tham số của hàm.
#
# - Nếu khai báo thiếu {}, FastAPI sẽ hiểu đó là đường dẫn cố định
#   chứ không phải là biến.
#
# - Path Parameter thường được sử dụng để lấy thông tin chi tiết của
#   một tài nguyên theo ID.
#
# - Nếu tìm thấy sản phẩm thì trả về thông tin sản phẩm.
#
# - Nếu không tìm thấy sản phẩm thì trả về lỗi 404 cùng thông báo rõ ràng.
#
# - Nếu người dùng nhập sai kiểu dữ liệu (ví dụ: abc), FastAPI sẽ tự động
#   báo lỗi validate vì product_id được khai báo là kiểu int.