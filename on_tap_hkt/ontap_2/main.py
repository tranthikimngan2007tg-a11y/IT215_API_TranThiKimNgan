from fastapi import FastAPI, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db, Base, engine
import models



app = FastAPI(
    title = "BUILD API FOR WORLD CUP TEAM MANAGEMENT",
    description = "XÂY DỰNG API QUẢN LÝ ĐỘI TUYỂN WORLD CUP"
)

Base.metadata.create_all(bind = engine)

@app.get("/")
def get_root(db: Session = Depends(get_db)):
    try:
        db.execute(text('SELECT 1'))
        return {
            "message": "Ket noi thanh cong!"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Khong the ket noi {str(e)}")
    

@app.get("/teams", tags=["Teams"], status_code=status.HTTP_200_OK)
def get_all_team(db: Session = Depends(get_db)):
