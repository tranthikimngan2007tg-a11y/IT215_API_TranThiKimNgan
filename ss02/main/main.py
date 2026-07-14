from fastapi import FastAPI

app = FastAPI(
    title="API quản lý sinh viên"
)

@app.get("/")
def get_root():
    return{"message": "Lấy dữ liệu thành công"}