from fastapi import FastAPI, Depends, Request
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from database import Base, engine, get_db
from model import SmartHomePlanModel
from smart_home_dto import (
    SmartHomePlanRequestDTO,
    APIResponse
)

from smart_home_service import (
    create_smart_home_plan,
    get_all_smart_home_plans,
    get_smart_home_plan_by_id
)


app = FastAPI(
    title="Smart Home Plans API"
)


Base.metadata.create_all(bind=engine)


@app.post(
    "/smart-home-plans",
    response_model=APIResponse,
    tags=["Smart Home Plans"]
)
def add_smart_home_plan(
    request: Request,
    plan: SmartHomePlanRequestDTO,
    db: Session = Depends(get_db)
):

    result = create_smart_home_plan(db, plan)

    return APIResponse(
        statusCode=201,
        message="Thêm gói thiết bị thành công",
        error=None,
        data={
            "id": result.id,
            "plan_code": result.plan_code,
            "plan_name": result.plan_name,
            "device_quantity": result.device_quantity,
            "price": result.price
        },
        path=request.url.path,
        timestamp=datetime.now(timezone.utc)
    )


@app.get(
    "/smart-home-plans",
    response_model=APIResponse,
    tags=["Smart Home Plans"]
)
def get_smart_home_plans(
    request: Request,
    db: Session = Depends(get_db)
):

    result = get_all_smart_home_plans(db)

    data = []

    for item in result:
        data.append({
            "id": item.id,
            "plan_code": item.plan_code,
            "plan_name": item.plan_name,
            "device_quantity": item.device_quantity,
            "price": item.price
        })


    return APIResponse(
        statusCode=200,
        message="Lấy danh sách thành công",
        error=None,
        data=data,
        path=request.url.path,
        timestamp=datetime.now(timezone.utc)
    )



@app.get(
    "/smart-home-plans/{plan_id}",
    response_model=APIResponse,
    tags=["Smart Home Plans"]
)
def get_smart_home_plan_detail(
    plan_id: int,
    request: Request,
    db: Session = Depends(get_db)
):

    result = get_smart_home_plan_by_id(
        db,
        plan_id
    )

    return APIResponse(
        statusCode=200,
        message="Lấy thông tin chi tiết thành công",
        error=None,
        data={
            "id": result.id,
            "plan_code": result.plan_code,
            "plan_name": result.plan_name,
            "device_quantity": result.device_quantity,
            "price": result.price
        },
        path=request.url.path,
        timestamp=datetime.now(timezone.utc)
    )