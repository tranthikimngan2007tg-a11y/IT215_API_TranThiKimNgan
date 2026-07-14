from sqlalchemy.orm import Session
from models import Product


def get_products(db: Session):
    return db.query(Product).all()


def get_product(db: Session, product_id: int):
    return db.query(Product).filter(Product.id == product_id).first()


def create_product(db: Session, product):
    new_product = Product(
        name=product.name,
        price=product.price
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product


def update_product(db: Session, product_id: int, product):
    old_product = db.query(Product).filter(Product.id == product_id).first()

    if old_product:
        old_product.name = product.name
        old_product.price = product.price

        db.commit()
        db.refresh(old_product)

    return old_product


def delete_product(db: Session, product_id: int):
    product = db.query(Product).filter(Product.id == product_id).first()

    if product:
        db.delete(product)
        db.commit()

    return product