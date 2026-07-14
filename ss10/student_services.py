from sqlalchemy.orm import Session
from model import StudentRequestDTO, StudentModel
from fastapi import HTTPException


def create_student(db: Session, student: StudentRequestDTO):
    try:
        new_student = StudentModel(
            id=student.id,
            full_name=student.full_name,
            email=student.email
        )

        db.add(new_student)
        db.commit()
        db.refresh(new_student)

        return {
            "status_code": 201,
            "message": "Thêm thành công",
            "data": new_student
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi thêm sinh viên: {str(e)}"
        )