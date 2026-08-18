from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="FlashMove RBAC + CORS")

ALLOWED_ORIGINS = [
    "https://driver.flashmove.io",
    "https://hub.flashmove.io",
]

ALLOWED_METHODS = ["GET", "POST", "PATCH"]
ALLOWED_HEADERS = ["Content-Type", "X-Role-Identity"]

# CORS whitelist nghiêm ngặt: tuyệt đối không dùng allow_origins=["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=ALLOWED_METHODS,
    allow_headers=ALLOWED_HEADERS,
    allow_credentials=False,
)


# Endpoint -> các role được phép
ROLE_RULES = {
    ("POST", "/api/v1/orders/assign"): {"DISPATCHER"},
    ("PATCH", "/api/v1/orders/status"): {"DISPATCHER", "DRIVER"},
    ("GET", "/api/v1/orders/track"): {
        "DISPATCHER",
        "DRIVER",
        "CUSTOMER_SUPPORT",
    },
}


@app.middleware("http")
async def role_middleware(request: Request, call_next):
    # OPTIONS là CORS preflight, không được yêu cầu role tại đây.
    # CORSMiddleware sẽ xử lý preflight trước khi request thật đi tiếp.
    if request.method == "OPTIONS":
        return await call_next(request)

    route_path = request.url.path
    route_key = (request.method, route_path)
    allowed_roles = ROLE_RULES.get(route_key)

    # Chỉ kiểm tra các endpoint nằm trong ROLE_RULES.
    if allowed_roles is not None:
        role = request.headers.get("X-Role-Identity")

        if role not in allowed_roles:
            return JSONResponse(
                status_code=403,
                content={
                    "status": "Rejected",
                    "reason": "Unauthorized action for this role",
                },
            )

    response = await call_next(request)
    response.headers["X-System-Name"] = "FlashMove Logistics"
    return response


@app.post("/api/v1/orders/assign")
async def assign_order():
    return {
        "status": "OK",
        "message": "Order assigned successfully",
    }


@app.patch("/api/v1/orders/status")
async def update_order_status():
    return {
        "status": "OK",
        "message": "Order status updated successfully",
    }


@app.get("/api/v1/orders/track")
async def track_order():
    return {
        "status": "OK",
        "message": "Order tracking data",
    }


@app.get("/health")
async def health():
    return {
        "status": "UP",
        "service": "FlashMove API",
    }
