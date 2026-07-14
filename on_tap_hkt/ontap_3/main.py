from fastapi import FastAPI, Depends, status, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from database import get_db, Base, engine

app = FastAPI(
    title = "Develop a centralized equipment inventory management system",
    description = "Xây dựng một hệ thống quản lý kho thiết bị tập trung"
)

Base.metadata.create_all(bind = engine)

@app.get("/test-connection")
def test_connection(db: Session = Depends(get_db)):
    try:
        db.execute(text('Select 1'))
        return {
            "message": "Ket noi thanh cong!"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Khong the ket noi {str(e)}")