from sqlalchemy.orm import Session
from app.cores.security import (
    create_access_token,
    hash_password,
    verify_password
)

from app.models.user import User


def get_user_by_username(
    db: Session,
    username: str
):

    return db.query(User).filter(
        User.username == username
    ).first()


def register_user(
    db: Session,
    username: str,
    password: str
):

    existing_user = get_user_by_username(
        db,
        username
    )

    if existing_user:
        return None

    hashed_password = hash_password(
        password
    )

    new_user = User(
        username=username,
        hashed_password=hashed_password
    )

    db.add(new_user)

    db.commit()

    db.refresh(new_user)

    return new_user


def authenticate_user(
    db: Session,
    username: str,
    password: str
):

    user = get_user_by_username(
        db,
        username
    )

    if not user:
        return None

    password_correct = verify_password(
        password,
        user.hashed_password
    )

    if not password_correct:
        return None

    return user


def login_user(
    db: Session,
    username: str,
    password: str
):

    user = authenticate_user(
        db,
        username,
        password
    )

    if not user:
        return None

    token = create_access_token(
        user.username
    )

    return token