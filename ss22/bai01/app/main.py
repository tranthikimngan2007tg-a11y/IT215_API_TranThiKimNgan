from fastapi import FastAPI
from app.db.database import Base, engine
from app.models.user import User
from app.routers.auth import router as auth_router


Base.metadata.create_all(
    bind=engine
)



app = FastAPI(
    title="DevConnect Authentication API",
    description="Secure Authentication using Bcrypt and JWT",
    version="1.0.0"
)


app.include_router(
    auth_router
)


@app.get("/")
def root():

    return {
        "message": "DevConnect Authentication API is running"
    }