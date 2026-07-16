from sqlalchemy.orm import Session

from models import Clinic, Doctor, License
from schemas import ClinicCreate, DoctorUpdate

def create_clinic(db: Session, clinic: ClinicCreate):

    try:
        # Giải nén dữ liệu từ Schema để tạo đối tượng Clinic
        new_clinic = Clinic(**clinic.model_dump())

        db.add(new_clinic)
        db.commit()
        db.refresh(new_clinic)

        return new_clinic

    except Exception:
        db.rollback()
        raise

def get_clinic_by_id(db: Session, clinic_id: int):

    clinic = db.query(Clinic).filter(Clinic.id == clinic_id).first()

    return clinic

def update_doctor(db: Session, doctor_id: int, doctor_update: DoctorUpdate):

    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()

    if doctor is None:
        return None

    try:
        update_data = doctor_update.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(doctor, key, value)

        db.commit()
        db.refresh(doctor)

        return doctor

    except Exception:
        db.rollback()
        raise

def delete_license(db: Session, license_id: int):

    license = db.query(License).filter(License.id == license_id).first()

    if license is None:
        return None

    try:

        db.delete(license)

        db.commit()

        return {"message": "Delete successfully"}

    except Exception:
        db.rollback()
        raise