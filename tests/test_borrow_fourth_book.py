import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException
from app.main import app
from app.models import User, Book, Reader
from app.crud import crud_books, crud_borrowed_books
from app.database import SessionLocal
from app.schemas import BookCreate
import uuid

client = TestClient(app)


@pytest.fixture
def db():
    db = SessionLocal()
    try:
        db.query(User).delete()
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

    # создаем книгу
    book = Book(title="Test Book", author="Author", copies=5)
    db.add(book)
    db.commit()
    db.refresh(book)

    # создаем читателя
    reader = Reader(name="Reader Name", email=f"reader_{uuid.uuid4()}@example.com")
    db.add(reader)
    db.commit()
    db.refresh(reader)

    return user, book, reader


def test_borrow_fourth_book(db, mock_data):
    user, book, reader = mock_data

    # 1. Имитация добавления книги в БД
    book_create = BookCreate(title=book.title, author=book.author, copies=book.copies)
    crud_books.create_book(db, book_create)
    crud_borrowed_books.issue_book(db, book.id, reader.id, user.id)
    crud_borrowed_books.issue_book(db, book.id, reader.id, user.id)
    crud_borrowed_books.issue_book(db, book.id, reader.id, user.id)

    # 2. Проверка попытки взять 4-ю книгу
    with pytest.raises(HTTPException, match="Reader has already borrowed 3 books"):
        crud_borrowed_books.issue_book(db, book.id, reader.id, user.id)
