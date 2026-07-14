from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from models import MenuItem
from schemas import (
    MenuItemRequestDTO,
    MenuItemUpdateDTO
)


def create_menu_item(
    menu_item: MenuItemRequestDTO,
    db: Session
):
    try:
        check_item = db.query(MenuItem).filter(
            MenuItem.dish_code == menu_item.dish_code
        ).first()

        if check_item:
            return None

        new_item = MenuItem(
            dish_code=menu_item.dish_code,
            dish_name=menu_item.dish_name,
            calorie_count=menu_item.calorie_count,
            price=menu_item.price,
            status=menu_item.status
        )

        db.add(new_item)
        db.commit()
        db.refresh(new_item)

        return new_item

    except SQLAlchemyError as s:
        db.rollback()
        raise s


def get_all_menu_items(db: Session):
    return db.query(MenuItem).all()


def get_menu_item_by_id(
    item_id: int,
    db: Session
):
    return db.query(MenuItem).filter(
        MenuItem.id == item_id
    ).first()
def update_menu_item(
    item_id: int,
    menu_item: MenuItemUpdateDTO,
    db: Session
):
    try:
        db_item = db.query(MenuItem).filter(
            MenuItem.id == item_id
        ).first()

        if not db_item:
            return None

        update_data = menu_item.model_dump(exclude_unset=True)

        if "dish_code" in update_data:
            check_item = db.query(MenuItem).filter(
                MenuItem.dish_code == update_data["dish_code"],
                MenuItem.id != item_id
            ).first()

            if check_item:
                return False

        for key, value in update_data.items():
            setattr(db_item, key, value)

        db.commit()
        db.refresh(db_item)

        return db_item

    except SQLAlchemyError as s:
        db.rollback()
        raise s


def delete_menu_item(
    item_id: int,
    db: Session
):
    try:
        db_item = db.query(MenuItem).filter(
            MenuItem.id == item_id
        ).first()

        if not db_item:
            return None

        db.delete(db_item)
        db.commit()

        return db_item

    except SQLAlchemyError as s:
        db.rollback()
        raise s