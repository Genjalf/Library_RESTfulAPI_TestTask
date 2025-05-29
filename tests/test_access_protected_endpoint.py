import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import User, Book, BorrowedBook
from app.auth import create_access_token
from app.database import SessionLocal
import uuid

client = TestClient(app)


@pytest.fixture
def db():
    db = SessionLocal()
    try:
        db.query(BorrowedBook).delete()
        db.query(User).delete()  # Удалить пользователей
        db.query(Book).delete()  # Удалить книги
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

    # создаем тестовую книгу
    book = Book(title="Test Book", author="Author", copies=5)
    db.add(book)
    db.commit()
    db.refresh(book)

    return user, book


@pytest.fixture
def valid_token(mock_data):
    # создаем валидный токен для тестирования
    return create_access_token(data={"sub": mock_data[0].email})


def test_get_books_with_token(db, mock_data, valid_token):
    # Получаем доступ к эндпоинту для получения книг с токеном
    response = client.get("/books/", headers={"Authorization": f"Bearer {valid_token}"})
    assert response.status_code == 200
    assert len(response.json()) > 0  # Проверяем, что в ответе есть книги


def test_get_books_with_invalid_token(db):
    invalid_token = "invalid_token"
    response = client.get(
        "/books/", headers={"Authorization": f"Bearer {invalid_token}"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}


def test_get_books_without_token(db, mock_data):
    # Попытка доступа к эндпоинту для получения книг без токена
    response = client.get("/books/")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}
