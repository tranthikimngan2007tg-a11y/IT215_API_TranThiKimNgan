from fastapi import FastAPI
from app.database import Base, engine
from app.models.student import Student
from app.routers.student import router as student_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Student Management API")
app.include_router(student_router)


@app.get("/")
def root():
    return {"message": "Student Management API is running"}
