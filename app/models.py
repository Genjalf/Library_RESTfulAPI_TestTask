from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


# модель для пользователей (библиотекарей)
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    # связь с таблицей BorrowedBooks
    borrowed_books = relationship("BorrowedBook", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"


# модель для книг
class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String, index=True)
    year = Column(Integer, nullable=True)
    isbn = Column(String, unique=True, nullable=True)
    copies = Column(Integer, default=1)
    description = Column(String, nullable=True)

    # связь с таблицей BorrowedBooks
    borrowed_books = relationship("BorrowedBook", back_populates="book")


# модель для читателей
class Reader(Base):
    __tablename__ = "readers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True)

    # связь с таблицей BorrowedBooks
    borrowed_books = relationship("BorrowedBook", back_populates="reader")


# модель для выданных книг
class BorrowedBook(Base):
    __tablename__ = "borrowed_books"

    id = Column(Integer, primary_key=True, index=True)
    borrow_date = Column(DateTime(timezone=True), server_default=func.now())
    return_date = Column(DateTime(timezone=True), nullable=True)

    book_id = Column(Integer, ForeignKey("books.id"))
    reader_id = Column(Integer, ForeignKey("readers.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    # связи с другими таблицами
    book = relationship("Book", back_populates="borrowed_books")
    reader = relationship("Reader", back_populates="borrowed_books")
    user = relationship("User", back_populates="borrowed_books")
