from schema import BookRequestlDTO
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models import BookModel


def create_book(db: Session , book: BookRequestlDTO):
    try:
        new_book = BookModel(
            id = book.id,
            title = book.title,
            author = book.author,
            isbn = book.isbn,
            status = book.status
        )
        db.add(new_book)
        db.commit()
        db.refresh(new_book)
        return new_book
    except SQLAlchemyError as s:
        db.rollback()
        raise s
