# Phần 1. Test case
# STT Dữ liệu gửi lên	Kết quả hiện tại (Mã HTTP + Body)	Kết quả đúng mong muốn	Lỗi phát hiện
# 1 GET /orders/999	HTTP 200 OK
# {"message":"Order not found"}	HTTP 404 Not Found
# {"detail":"Order not found"}	API trả về sai mã trạng thái HTTP. Không tìm thấy đơn hàng nhưng vẫn trả về 200 OK.
# 2	GET /orders/1	HTTP 200 OK
# {"id":1,"customer_name":"Nguyen Van A","total_amount":1500000.0,"profit_margin":0.25,"supplier_id":"SUP_DELL_01"}	HTTP 200 OK
# {"id":1,"customer_name":"Nguyen Van A","total_amount":1500000.0}	API trả về dữ liệu nhạy cảm là profit_margin và supplier_id, vi phạm yêu cầu bảo mật.
# Phần 2. Code sau khi sửa
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

orders_db = [
    {
        "id": 1,
        "customer_name": "Nguyen Van A",
        "total_amount": 1500000.0,
        "profit_margin": 0.25,
        "supplier_id": "SUP_DELL_01"
    },
    {
        "id": 2,
        "customer_name": "Tran Thi B",
        "total_amount": 350000.0,
        "profit_margin": 0.30,
        "supplier_id": "SUP_LOGI_02"
    }
]

class OrderResponse(BaseModel):
    id: int
    customer_name: str
    total_amount: float

@app.get("/orders/{order_id}", response_model=OrderResponse)
def get_order_detail(order_id: int):
    for order in orders_db:
        if order["id"] == order_id:
            return {
                "id": order["id"],
                "customer_name": order["customer_name"],
                "total_amount": order["total_amount"]
            }

    raise HTTPException(
        status_code=404,
        detail="Order not found"
    )