from fastapi import FastAPI, Depends, status, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from database import Base, get_db, engine
import models
import crud
from schema import BookRequestlDTO

app = FastAPI(
    title = "LIBRARY MANAGEMENT API",
    description = "XÂY DỰNG HỆ THỐNG QUẢN LÝ MƯỢN TRẢ SÁCH" 
)

Base.metadata.create_all(bind = engine)

# @app.get("/test-connection")
# def test_connection(db: Session = Depends(get_db)):
#     try:
#         db.execute(text('SELECT 1'))
#         return {
#             "message": "Kết nối thành công!"
#         }
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Không thể kết nối {str(e)}")

@app.post("/book", tags = ["Book"], status_code=status.HTTP_201_CREATED)
def add_book(book: BookRequestlDTO, db: Session = Depends(get_db)):
    db_book = crud.create_book(db, book)
    if not db_book:
        raise HTTPException(status_code=404, detail="Them sach khong thanh cong!")
    return {
        "status_code": 201,
        "message": "Them sach thanh cong!",
        "data": db_book
    }