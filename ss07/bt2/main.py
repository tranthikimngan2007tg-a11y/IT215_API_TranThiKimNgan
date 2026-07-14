# Phần 1. Test case
# STT	Dữ liệu/Endpoint gửi lên	Kết quả hiện tại (Mã HTTP + Body)	Kết quả đúng mong muốn	Lỗi phát hiện
# 1	PUT /orders/999/status
# Body: {"status":"SHIPPING"}	HTTP 200 OK
# {"statusCode":200,"message":"Cập nhật thành công","data":null}	HTTP 404 Not Found
# {"detail":"Order not found"}	Khi order_id không tồn tại, chương trình chỉ print() mà không dừng xử lý, vẫn trả về 200 OK.
# 2	PUT /orders/1/status
# Body: {"status":"TRONG_SANG"}	HTTP 200 OK
# {"error":"Trạng thái không hợp lệ"}	HTTP 400 Bad Request
# {"detail":"Trạng thái không hợp lệ"}	API xử lý lỗi bằng return thay vì raise HTTPException, đồng thời dùng chuỗi trạng thái (Magic Number/Magic String) viết trực tiếp trong code.
# Phần 2. Code sau khi sửa
from enum import Enum

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

orders_db = [
    {"id": 1, "customer_name": "Nguyen Van A", "status": "PENDING"},
    {"id": 2, "customer_name": "Tran Thi B", "status": "SHIPPING"}
]


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    SHIPPING = "SHIPPING"
    DELIVERED = "DELIVERED"


class StatusUpdate(BaseModel):
    status: OrderStatus


@app.get("/orders/{order_id}")
def get_order(order_id: int):
    order = next((o for o in orders_db if o["id"] == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@app.put("/orders/{order_id}/status")
def update_order_status(order_id: int, data: StatusUpdate):
    order = next((o for o in orders_db if o["id"] == order_id), None)

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order["status"] = data.status.value

    return {
        "statusCode": 200,
        "message": "Cập nhật thành công",
        "data": order
    }