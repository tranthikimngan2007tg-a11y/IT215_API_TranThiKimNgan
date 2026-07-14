from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from database import get_db, init_db

app = FastAPI(title="SQLAlchemy FastAPI Demo")


@app.on_event("startup")
def startup_event():
    init_db()


@app.get("/")
def read_root():
    return {"message": "FastAPI đang chạy"}


@app.get("/test-connection")
def test_connection(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"message": "Kết nối thành công!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi không thể kết nối được: {e}")
