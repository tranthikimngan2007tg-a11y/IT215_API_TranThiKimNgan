from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.student import StudentCreate, StudentResponse, StudentUpdate
from app.services.student import (
    create_student,
    delete_student,
    get_all_students,
    get_student_by_id,
    update_student,
)

router = APIRouter()


@router.get("/students", response_model=list[StudentResponse])
def list_students(db: Session = Depends(get_db)):
    return get_all_students(db)


@router.get("/students/{student_id}", response_model=StudentResponse)
def read_student(student_id: int, db: Session = Depends(get_db)):
    return get_student_by_id(db, student_id)


@router.post("/students", response_model=StudentResponse)
def create_student_endpoint(student_data: StudentCreate, db: Session = Depends(get_db)):
    return create_student(db, student_data)


@router.put("/students/{student_id}", response_model=StudentResponse)
def update_student_endpoint(student_id: int, student_data: StudentUpdate, db: Session = Depends(get_db)):
    return update_student(db, student_id, student_data)


@router.delete("/students/{student_id}")
def delete_student_endpoint(student_id: int, db: Session = Depends(get_db)):
    return delete_student(db, student_id)
