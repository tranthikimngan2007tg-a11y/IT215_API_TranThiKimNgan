from fastapi import FastAPI, Depends, status
from sqlalchemy.orm import Session

import crud
import schemas
from database import Base, engine, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI()


# Student


@app.post(
    "/students",
    response_model=schemas.StudentResponse,
    status_code=status.HTTP_201_CREATED
)
def create_student(
    student: schemas.StudentCreate,
    db: Session = Depends(get_db)
):
    return crud.create_student(db, student)


@app.get(
    "/students",
    response_model=list[schemas.StudentResponse]
)
def get_students(db: Session = Depends(get_db)):
    return crud.get_students(db)


# ==========================
# Workshop
# ==========================

@app.post(
    "/workshops",
    response_model=schemas.WorkshopResponse,
    status_code=status.HTTP_201_CREATED
)
def create_workshop(
    workshop: schemas.WorkshopCreate,
    db: Session = Depends(get_db)
):
    return crud.create_workshop(db, workshop)


@app.get(
    "/workshops",
    response_model=list[schemas.WorkshopResponse]
)
def get_workshops(db: Session = Depends(get_db)):
    return crud.get_workshops(db)


@app.get(
    "/workshops/{workshop_id}",
    response_model=schemas.WorkshopResponse
)
def get_workshop(
    workshop_id: int,
    db: Session = Depends(get_db)
):
    return crud.get_workshop(db, workshop_id)


# ==========================
# Registration
# ==========================

@app.post(
    "/registrations",
    response_model=schemas.RegistrationResponse,
    status_code=status.HTTP_201_CREATED
)
def create_registration(
    registration: schemas.RegistrationCreate,
    db: Session = Depends(get_db)
):
    return crud.create_registration(db, registration)


@app.get(
    "/students/{student_id}/workshops",
    response_model=schemas.StudentWorkshopsResponse
)
def get_student_workshops(
    student_id: int,
    db: Session = Depends(get_db)
):
    return crud.get_student_workshops(db, student_id)


@app.get(
    "/workshops/{workshop_id}/students",
    response_model=schemas.WorkshopStudentsResponse
)
def get_workshop_students(
    workshop_id: int,
    db: Session = Depends(get_db)
):
    return crud.get_workshop_students(db, workshop_id)


@app.put("/registrations/{registration_id}")
def cancel_registration(
    registration_id: int,
    db: Session = Depends(get_db)
):
    return crud.cancel_registration(db, registration_id)

