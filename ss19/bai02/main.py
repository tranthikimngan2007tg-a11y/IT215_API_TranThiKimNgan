from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from schemas import (
    ClinicCreate,
    ClinicDetailResponse,
    DoctorUpdate,
    DoctorResponse
)
from service import create_clinic, get_clinic_by_id, update_doctor, delete_license



import models

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post(
    "/clinics",
    status_code=status.HTTP_201_CREATED
)
def create_new_clinic(
    clinic: ClinicCreate,
    db: Session = Depends(get_db)
):
    return create_clinic(db, clinic)

@app.get(
    "/clinics/{clinic_id}",
    response_model=ClinicDetailResponse
)
def get_clinic(
    clinic_id: int,
    db: Session = Depends(get_db)
):

    clinic = get_clinic_by_id(db, clinic_id)

    if clinic is None:
        raise HTTPException(
            status_code=404,
            detail="Clinic not found"
        )

    return clinic


@app.patch(
    "/doctors/{doctor_id}",
    response_model=DoctorResponse
)
def update(
    doctor_id: int,
    doctor: DoctorUpdate,
    db: Session = Depends(get_db)
):

    result = update_doctor(db, doctor_id, doctor)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    return result

@app.delete("/licenses/{license_id}")
def delete(
    license_id: int,
    db: Session = Depends(get_db)
):

    result = delete_license(db, license_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="License not found"
        )

    return result