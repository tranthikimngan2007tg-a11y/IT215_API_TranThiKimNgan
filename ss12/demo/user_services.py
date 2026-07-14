from sqlalchemy.orm import Session
from schemas import UserRequestDTO
from models import UserModel
from sqlalchemy.exc import SQLAlchemyError

# Viet ham them du lieu
def create_user(db: Session, user: UserRequestDTO):
    try:
        new_user = UserModel(
            name = user.name,
            email = user.email
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except SQLAlchemyError as s:
        db.rollback()
        raise s

# Viet ham lay du lieu
def get_user(db: Session, user_id: int):
    return db.query(UserModel).filter(UserModel.id == user_id).first()        

# Viet ham cap nhat du lieu
def update_user(db: Session, user_id: int, user: UserRequestDTO):
    try:
        db_user = get_user(db, user_id)
        if not db_user:
            return None
        db_user.name = user.name
        db_user.email = user.email
        db.commit()
        db.refresh(db_user)
        return db_user
    except SQLAlchemyError as s:
        db.rollback()
        raise s
