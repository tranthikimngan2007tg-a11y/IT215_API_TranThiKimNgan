from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials
)

from app.cores.security import (
    decode_access_token
)

from app.schemas.prescription import (
    PrescriptionCreate
)


router = APIRouter(
    prefix="/api/v1/prescriptions",
    tags=["Prescriptions"]
)


security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        security
    )
):

    token = credentials.credentials

    payload = decode_access_token(
        token
    )

    username = payload.get("sub")

    role = payload.get("role")

    if not username or not role:

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    return {
        "username": username,
        "role": role
    }


@router.post("")
def create_prescription(
    data: PrescriptionCreate,
    user: dict = Depends(
        get_current_user
    )
):

    if user["role"] != "doctor":

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không đủ quyền hạn"
        )

    return {
        "message": "Tạo đơn thuốc thành công",
        "doctor": user["username"],
        "patient_name": data.patient_name,
        "medicine": data.medicine,
        "dosage": data.dosage
    }


@router.get("/view")
def view_prescription(
    user: dict = Depends(
        get_current_user
    )
):

    return {
        "message": "Xem đơn thuốc thành công",
        "username": user["username"],
        "role": user["role"]
    }