from sqlalchemy.orm import Session
from app import models as m, schemas as s
from datetime import datetime
from app.crud.crud_books import get_book
from app.crud.crud_readers import get_reader
from fastapi import HTTPException
from typing import Optional


# создание выданной книги
def create_borrowed_book(
    db: Session,
    borrowed_book: s.BorrowedBookCreate,
) -> m.BorrowedBook:

    db_borrowed_book = m.BorrowedBook(**borrowed_book.dict())
    db.add(db_borrowed_book)
    db.commit()
    db.refresh(db_borrowed_book)
    return db_borrowed_book


# получение всех выданных книг
def get_all_borrowed_books(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[m.BorrowedBook]:

    return db.query(m.BorrowedBook).offset(skip).limit(limit).all()


# получение выданной книги по ID
def get_borrowed_book(db: Session, bbook_id: int) -> Optional[m.BorrowedBook]:
    return db.query(m.BorrowedBook).filter(m.BorrowedBook.id == bbook_id).first()


# обновление выданной книги
def update_borrowed_book(
    db: Session,
    bbook_id: int,
    bbook_data: s.BorrowedBookCreate,
) -> Optional[m.BorrowedBook]:

    db_borrowed_book = get_borrowed_book(db, bbook_id)
    if not db_borrowed_book:
        return None
    for key, value in bbook_data.dict().items():
        setattr(db_borrowed_book, key, value)
    db.commit()
    db.refresh(db_borrowed_book)
    return db_borrowed_book


# удаление выданной книги
def delete_borrowed_book(db: Session, bbook_id: int) -> Optional[m.BorrowedBook]:
    db_borrowed_book = get_borrowed_book(db, bbook_id)
    if not db_borrowed_book:
        return None
    db.delete(db_borrowed_book)
    db.commit()
    return db_borrowed_book


# получение всех выданных книг по читателю
def get_all_borrowed_books_by_reader(
    db: Session,
    reader_id: int,
) -> list[m.BorrowedBook]:

    return db.query(m.BorrowedBook).filter(m.BorrowedBook.reader_id == reader_id).all()


# получение выданных книг по читателю
# получаем только книги, которые читатель ещё не вернул
def get_unreturned_books_by_reader(
    db: Session,
    reader_id: int,
) -> list[m.BorrowedBook]:

    return (
        db.query(m.BorrowedBook)
        .filter(
            m.BorrowedBook.reader_id == reader_id, m.BorrowedBook.return_date.is_(None)
        )
        .all()
    )


# выдача книги
# только если книга есть в наличии
# читателю нельзя иметь более трех книг одновременно
def issue_book(
    db: Session,
    book_id: int,
    reader_id: int,
    user_id: int,
) -> Optional[m.BorrowedBook]:

    # получаем книгу
    book = get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if book.copies <= 0:
        raise HTTPException(status_code=400, detail="No available copies")

    # получаем читателя
    reader = get_reader(db, reader_id)
    if not reader:
        raise HTTPException(status_code=404, detail="Reader not found")

    # проверяем по количеству книг у читателя
    # нельзя выдавать книгу, если у читателя уже есть 3 книги
    if len(get_unreturned_books_by_reader(db, reader_id)) >= 3:
        raise HTTPException(
            status_code=400, detail="Reader has already borrowed 3 books"
        )

    # создаем запись о выданной книге
    borrowed_book = m.BorrowedBook(
        book_id=book.id,
        reader_id=reader.id,
        user_id=user_id,
        borrow_date=datetime.utcnow(),
    )
    db.add(borrowed_book)
    book.copies -= 1
    db.commit()
    db.refresh(borrowed_book)
    return borrowed_book


# возврат книги
def return_book(
    db: Session,
    reader_id: int,
    book_id: int,
    bbook_id: int,
) -> Optional[m.BorrowedBook]:

    # получаем читателя
    reader = get_reader(db, reader_id)
    if not reader:
        raise HTTPException(status_code=404, detail="Reader not found")

    # получаем книгу
    book = get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    # получаем запись о выдаче книги
    bbook = get_borrowed_book(db, bbook_id)
    if not bbook:
        raise HTTPException(status_code=404, detail="Borrowed book not found")

    # проверяем, та ли это книга и тот ли это читатель
    if bbook.book_id != book_id or bbook.reader_id != reader_id:
        raise HTTPException(
            status_code=400, detail="This book was not borrowed by this reader"
        )

    # проверяем, не возвращена ли уже книга
    if bbook.return_date:
        raise HTTPException(status_code=400, detail="Book already returned")

    # возвращаем книгу
    bbook.return_date = datetime.utcnow()
    book.copies += 1
    db.commit()
    db.refresh(bbook)
    return bbook
