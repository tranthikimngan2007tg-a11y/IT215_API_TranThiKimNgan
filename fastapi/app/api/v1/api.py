from fastapi import APIRouter
from app.api.v1 import auth, classes, students, scores

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(classes.router, prefix="/classes", tags=["Classes"])
api_router.include_router(students.router, prefix="/students", tags=["Students"])
api_router.include_router(scores.router, prefix="/scores", tags=["Scores"])
