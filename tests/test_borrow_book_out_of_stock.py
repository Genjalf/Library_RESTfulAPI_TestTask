import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException
from app.main import app
from app.models import User, Book, Reader, BorrowedBook
from app.crud import crud_borrowed_books
from app.database import SessionLocal
import uuid

client = TestClient(app)


@pytest.fixture
def db():
    db = SessionLocal()
    try:
        db.query(BorrowedBook).delete()  # Удалить заимствованные книги
        db.query(User).delete()  # Удалить пользователей
        db.query(Book).delete()  # Удалить книги
        db.query(Reader).delete()  # Удалить читателей
        db.commit()
        yield db
    finally:
        db.close()


@pytest.fixture
def mock_data(db):
    # создаем тестового библиотекаря
    user = User(
        email=f"test_{uuid.uuid4()}@library.com", hashed_password="hashed_password"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # создаем книгу с 0 копиями
    book = Book(title="Test Book", author="Author", copies=0)
    db.add(book)
    db.commit()
    db.refresh(book)

    # создаем читателя
    reader = Reader(name="Reader Name", email=f"reader_{uuid.uuid4()}@example.com")
    db.add(reader)
    db.commit()
    db.refresh(reader)

    return user, book, reader


def test_borrow_book_out_of_stock(db, mock_data):
    user, book, reader = mock_data

    # 1. Попытка взять книгу, которой нет в наличии
    with pytest.raises(HTTPException, match="No available copies"):
        crud_borrowed_books.issue_book(db, book.id, reader.id, user.id)
