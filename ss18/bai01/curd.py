from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import datetime

import models
import schemas


# ==========================
# Student
# ==========================

def create_student(db: Session, student: schemas.StudentCreate):
    new_student = models.Student(
        student_code=student.student_code,
        full_name=student.full_name,
        email=student.email,
        status=student.status
    )

    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    return new_student


def get_students(db: Session):
    return db.query(models.Student).all()


# ==========================
# Workshop
# ==========================

def create_workshop(db: Session, workshop: schemas.WorkshopCreate):
    new_workshop = models.Workshop(
        title=workshop.title,
        description=workshop.description,
        maximum_participants=workshop.maximum_participants,
        status=workshop.status,
        start_time=workshop.start_time
    )

    db.add(new_workshop)
    db.commit()
    db.refresh(new_workshop)

    return new_workshop


def get_workshops(db: Session):
    return db.query(models.Workshop).all()


def get_workshop(db: Session, workshop_id: int):
    workshop = db.query(models.Workshop).filter(
        models.Workshop.id == workshop_id
    ).first()

    if not workshop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workshop not found"
        )

    return workshop


# ==========================
# Registration
# ==========================

def create_registration(db: Session, registration: schemas.RegistrationCreate):

    student = db.query(models.Student).filter(
        models.Student.id == registration.student_id
    ).first()

    # Kiểm tra sinh viên có tồn tại.
    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    workshop = db.query(models.Workshop).filter(
        models.Workshop.id == registration.workshop_id
    ).first()

    # Kiểm tra workshop có tồn tại.
    if not workshop:
        raise HTTPException(
            status_code=404,
            detail="Workshop not found"
        )

    # Chỉ sinh viên ACTIVE mới được đăng ký.
    if student.status != "ACTIVE":
        raise HTTPException(
            status_code=400,
            detail="Student is inactive"
        )

    # Chỉ workshop OPEN mới được đăng ký.
    if workshop.status != "OPEN":
        raise HTTPException(
            status_code=400,
            detail="Workshop is closed"
        )

    # Không cho phép đăng ký khi workshop đã bắt đầu.
    if workshop.start_time <= datetime.utcnow():
        raise HTTPException(
            status_code=400,
            detail="Workshop has already started"
        )

    existed = db.query(models.Registration).filter(
        models.Registration.student_id == registration.student_id,
        models.Registration.workshop_id == registration.workshop_id,
        models.Registration.status == "REGISTERED"
    ).first()

    # Không cho phép đăng ký trùng.
    if existed:
        raise HTTPException(
            status_code=400,
            detail="Student already registered"
        )

    total = db.query(func.count(models.Registration.id)).filter(
        models.Registration.workshop_id == registration.workshop_id,
        models.Registration.status == "REGISTERED"
    ).scalar()

    # Không cho phép vượt quá số lượng tối đa.
    if total >= workshop.maximum_participants:
        raise HTTPException(
            status_code=400,
            detail="Workshop is full"
        )

    new_registration = models.Registration(
        student_id=registration.student_id,
        workshop_id=registration.workshop_id
    )

    db.add(new_registration)
    db.commit()
    db.refresh(new_registration)

    return new_registration


def get_student_workshops(db: Session, student_id: int):

    student = db.query(models.Student).filter(
        models.Student.id == student_id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    workshops = (
        db.query(models.Workshop)
        .join(
            models.Registration,
            models.Workshop.id == models.Registration.workshop_id
        )
        .filter(
            models.Registration.student_id == student_id,
            models.Registration.status == "REGISTERED"
        )
        .all()
    )

    return {
        "student_id": student.id,
        "full_name": student.full_name,
        "workshops": workshops
    }


def get_workshop_students(db: Session, workshop_id: int):

    workshop = db.query(models.Workshop).filter(
        models.Workshop.id == workshop_id
    ).first()

    if not workshop:
        raise HTTPException(
            status_code=404,
            detail="Workshop not found"
        )

    students = (
        db.query(models.Student)
        .join(
            models.Registration,
            models.Student.id == models.Registration.student_id
        )
        .filter(
            models.Registration.workshop_id == workshop_id,
            models.Registration.status == "REGISTERED"
        )
        .all()
    )

    return {
        "workshop_id": workshop.id,
        "title": workshop.title,
        "students": students
    }


def cancel_registration(db: Session, registration_id: int):

    registration = db.query(models.Registration).filter(
        models.Registration.id == registration_id
    ).first()

    if not registration:
        raise HTTPException(
            status_code=404,
            detail="Registration not found"
        )

    registration.status = "CANCELLED"

    db.commit()
    db.refresh(registration)

    return {
        "message": "Registration cancelled successfully"
    }

