from sqlalchemy.orm import Session
from app.models.user import User
from app.cores.security import (
    hash_password,
    verify_password,
    create_access_token
)


def get_user(
    db: Session,
    username: str
):

    return db.query(User).filter(
        User.username == username
    ).first()

def register_user(
    db: Session,
    username: str,
    password: str,
    role: str
):

    old_user = get_user(
        db,
        username
    )

    if old_user:
        return None

    hashed_password = hash_password(
        password
    )

    user = User(
        username=username,
        hashed_password=hashed_password,
        role=role
    )

    db.add(user)

    db.commit()

    db.refresh(user)

    return user


def login_user(
    db: Session,
    username: str,
    password: str
):

    user = get_user(
        db,
        username
    )

    if not user:
        return None

    if not verify_password(
        password,
        user.hashed_password
    ):
        return None

    token = create_access_token(
        user.username,
        user.role
    )

    return token