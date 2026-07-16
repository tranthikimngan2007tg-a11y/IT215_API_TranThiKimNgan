from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from app.schemas import WarehouseCreate, PackageUpdate, PackageResponse
from  app.models import Warehouse, Package, Waybill


def create_warehouse(db : Session, warehouse : WarehouseCreate ):
   
    try:
        new_warehouse =  Warehouse(**warehouse.model_dump())
        db.add(new_warehouse)
        db.commit()
        db.refresh(new_warehouse)
        return new_warehouse
    except SQLAlchemyError: 
        db.rollback()
        raise HTTPException(status_code=500,detail="lỗi không xác định")


def get_warehouse(warehouse_id : int, db: Session):
    warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not warehouse:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="NOT FOUND")
    return warehouse

def update_package(package_id: int, package: PackageUpdate, db: Session):
    update_pkg = db.query(Package).filter(Package.id == package_id).first()
    if not update_pkg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    update_db = package.model_dump(exclude_unset=True)
    update_pkg.package_code = package.package_code
    update_pkg.weight = package.weight
    
    for key, value in update_db.items():
        setattr(update_pkg, key, value)
    db.commit()
    db.refresh(update_db)
    return update_db

def delete_waybill(waybill_id: int, db: Session):
    del_waybill = db.query(Waybill).filter(Waybill.id == waybill_id).first()
    if not del_waybill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="NOT FOUND")
    db.delete(del_waybill)
    db.commit()
    db.refresh(del_waybill)
    return del_waybill