from fastapi import FastAPI

from database import Base
from database import engine

from models import Product
from routers import router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Product Management API"
)

app.include_router(router)