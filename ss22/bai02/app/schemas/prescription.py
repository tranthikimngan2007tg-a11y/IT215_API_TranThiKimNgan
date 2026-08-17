from pydantic import BaseModel


class PrescriptionCreate(BaseModel):

    patient_name: str

    medicine: str

    dosage: str