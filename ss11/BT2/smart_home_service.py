from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from model import SmartHomePlanModel
from smart_home_dto import SmartHomePlanRequestDTO


def create_smart_home_plan(db: Session, plan: SmartHomePlanRequestDTO):
    try:
        new_plan = SmartHomePlanModel(
            plan_code=plan.plan_code,
            plan_name=plan.plan_name,
            device_quantity=plan.device_quantity,
            price=plan.price
        )

        db.add(new_plan)
        db.commit()
        db.refresh(new_plan)

        return new_plan

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Plan code already exists"
        )

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )


def get_all_smart_home_plans(db: Session):
    return db.query(SmartHomePlanModel).all()


def get_smart_home_plan_by_id(db: Session, plan_id: int):
    plan = db.query(SmartHomePlanModel).filter(
        SmartHomePlanModel.id == plan_id
    ).first()

    if plan is None:
        raise HTTPException(
            status_code=404,
            detail="Plan not found"
        )

    return plan