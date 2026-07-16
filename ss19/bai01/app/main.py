from fastapi import FastAPI, Depends , status
from app.database import Base,engine,get_db
from sqlalchemy.orm import Session
from app.schemas import WarehouseCreate, WarehouseDetailResponse, PackageUpdate
import app.services

app = FastAPI()
Base.metadata.create_all(bind=engine)

@app.post('/warehouses',status_code=status.HTTP_201_CREATED)
def create_warehouse(warehouse: WarehouseCreate, db : Session = Depends(get_db)):
    return app.services.create_warehouse(db=db,warehouse=warehouse,)
@app.get("/warehouses/{warehouse_id}",response_model=WarehouseDetailResponse, status_code=status.HTTP_200_OK)
def get_warehouse(warehouse_id: int, db : Session = Depends(get_db)):
    return app.services.get_warehouse(db=db,warehouse_id=warehouse_id)

@app.put("/packages/{package_id}")
def package_update(package: PackageUpdate, package_id = int ,db: Session = Depends(get_db)):
    return app.services.update_package(db=db, package_id=package_id, package=package)

@app.delete("/waybills/{waybill_id}")
def waybill_delete(waybill_id: int, db: Session):
    return app.services.delete_waybill(waybill_id=waybill_id, db=db)