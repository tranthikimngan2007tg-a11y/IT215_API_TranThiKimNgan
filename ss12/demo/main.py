from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db, Base, engine
from sqlalchemy import text
import models
from schemas import UserRequestDTO
import user_services

app = FastAPI(
    title = "Manager Users"
)

Base.metadata.create_all(bind = engine)

@app.get("/test-connection")
def test_connection(db: Session = Depends(get_db)):
    try:
        db.execute(text('SELECT 1'))
        return {
            "message": "Kết nối thành công!"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Không thể kết nối {str(e)}")

@app.post("/users", tags=["Users"], status_code=status.HTTP_201_CREATED)
def add_users(user: UserRequestDTO, db: Session = Depends(get_db)):
    db_user = user_services.create_user(db, user)
    if not db_user:
        raise HTTPException(status_code=404, detail= "Them du lieu khong thanh cong")
    return {
        "status_code": 201,
        "message": "Them thanh cong!",
        "data": db_user
    }

# API lay user
@app.get("/users/{user_id}", tags=["Users"])
def get_user(user_id: int, db: Session = Depends(get_db)):
    db_user = user_services.get_user(db, user_id)
    if not db_user:
        raise HTTPException (status_code=404, detail="ID Not Found")
    return {
        "status_code": 200,
        "message": "Lay du lieu thanh cong",
        "data": db_user
    }   

# API cap nhat user
@app.put("/users/{user_id}",tags=["Users"])
def update_user(user_id: int, user: UserRequestDTO, db: Session = Depends(get_db)):
    db_user = user_services.update_user(db, user_id, user)
    if not db_user:
        raise HTTPException (status_code=404, detail="Cap nhat that bai")
    return {
        "status_code": 200,
        "message": "Cap nhat thanh cong",
        "data": db_user
    }

