from fastapi import FastAPI

from database import Base, engine
import supply_chain_models

app = FastAPI(title="Supply Chain API")


@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)
    print("Tạo bảng thành công!")


@app.get("/")
def read_root():
    return {"message": "Supply Chain API is running"}