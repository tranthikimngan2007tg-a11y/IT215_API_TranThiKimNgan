from fastapi import FastAPI
from app.database.database import Base,engine


from app.models.user import User

from app.routers.auth import (
    router as auth_router
)

from app.routers.prescription import (
    router as prescription_router
)


# Tạo bảng
Base.metadata.create_all(
    bind=engine
)


app = FastAPI(
    title="MedCare API"
)


app.include_router(
    auth_router
)

app.include_router(
    prescription_router
)


@app.get("/")
def root():

    return {
        "message": "MedCare API is running"
    }