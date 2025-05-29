import pytest
from fastapi.testclient import TestClient
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

    # создаем книгу с 5 копиями
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


def test_return_borrowed_book(db, mock_data):
    user, book, reader = mock_data

    # 1. Выдача книги читателю
    crud_borrowed_books.issue_book(db, book.id, reader.id, user.id)

    # 2. Проверка, что книга была выдана
    borrowed_books = db.query(BorrowedBook).filter_by(reader_id=reader.id).all()
    assert len(borrowed_books) == 1
    assert borrowed_books[0].return_date is None  # Книга еще не возвращена
    assert book.copies == 4  # Количество доступных копий должно уменьшиться на 1

    # 3. Возврат книги
    borrowed_book = borrowed_books[0]
    response = crud_borrowed_books.return_book(db, reader.id, book.id, borrowed_book.id)

    # 4. Проверка возврата
    assert response.return_date is not None  # Дата возврата должна быть установлена

    # 5. Проверка, что количество копий увеличилось
    # Мы делаем запрос снова к базе данных, чтобы проверить актуальное значение.
    book = db.query(Book).filter_by(id=book.id).first()  # Запрос к базе
    assert (
        book.copies == 5
    )  # Количество доступных копий должно увеличиться обратно на 1
