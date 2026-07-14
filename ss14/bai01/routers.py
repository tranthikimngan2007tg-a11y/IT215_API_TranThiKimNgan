from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from database import get_db
from schemas import ProductCreate
from schemas import ProductResponse
import services

router = APIRouter()


@router.get("/products", response_model=list[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    return services.get_products(db)


@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = services.get_product(db, product_id)

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


@router.post("/products", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    return services.create_product(db, product)


@router.put("/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: int,
                   product: ProductCreate,
                   db: Session = Depends(get_db)):

    update = services.update_product(db, product_id, product)

    if update is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return update


@router.delete("/products/{product_id}")
def delete_product(product_id: int,
                   db: Session = Depends(get_db)):

    product = services.delete_product(db, product_id)

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return {"message": "Delete successfully"}