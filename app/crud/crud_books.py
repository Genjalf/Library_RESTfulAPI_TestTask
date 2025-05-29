from sqlalchemy.orm import Session
from app import models as m, schemas as s
from typing import Optional


# создание книги
def create_book(db: Session, book: s.BookCreate) -> m.Book:
    db_book = m.Book(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


# получение всех книг
def get_all_books(db: Session, skip: int = 0, limit: int = 100) -> list[m.Book]:
    return db.query(m.Book).offset(skip).limit(limit).all()


# получение книги по ID
def get_book(db: Session, book_id: int) -> Optional[m.Book]:
    return db.query(m.Book).filter(m.Book.id == book_id).first()


# обновление книги
def update_book(db: Session, book_id: int, book_data: s.BookCreate) -> Optional[m.Book]:
    db_book = get_book(db, book_id)
    if not db_book:
        return None
    for key, value in book_data.dict().items():
        setattr(db_book, key, value)
    db.commit()
    db.refresh(db_book)
    return db_book


# удаление книги
def delete_book(db: Session, book_id: int) -> Optional[m.Book]:
    db_book = get_book(db, book_id)
    if not db_book:
        return None
    db.delete(db_book)
    db.commit()
    return db_book
