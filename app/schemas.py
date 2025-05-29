from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# -------------------Библиотекари-------------------
# создание
class UserCreate(BaseModel):
    email: EmailStr
    password: str


# ответ
class UserResponse(BaseModel):
    id: int
    email: EmailStr

    class Config:
        orm_mode = True


# логин
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# -------------------Книги-----------------------


class BookBase(BaseModel):
    title: str
    author: str
    year: Optional[int] = None
    isbn: Optional[int] = None
    copies: int = 1


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    year: Optional[int] = None
    isbn: Optional[int] = None
    copies: Optional[int] = None


class BookResponse(BookBase):
    id: int

    class Config:
        orm_mode = True


class ReturnBookRequest(BaseModel):
    reader_id: int
    book_id: int
    bbook_id: int


# ---------Читатели---------


class ReaderBase(BaseModel):
    name: str
    email: EmailStr


# создание
class ReaderCreate(ReaderBase):
    pass


# обновление
class ReaderUpdate(ReaderBase):
    pass


# для ответа
class ReaderResponse(ReaderBase):
    id: int

    class Config:
        orm_mode = True


# ----------------------Выданные книги--------------------


class BorrowedBookBase(BaseModel):
    borrow_date: Optional[datetime]
    return_date: Optional[datetime] = None
    book_id: int
    reader_id: int
    user_id: int


# создание
class BorrowedBookCreate(BorrowedBookBase):
    pass


# обновление
class BorrowedBookUpdate(BorrowedBookBase):
    borrow_date: Optional[datetime] = None
    return_date: Optional[datetime] = None
    book_id: Optional[int] = None
    reader_id: Optional[int] = None
    user_id: Optional[int] = None


# для ответа
class BorrowedBookResponse(BorrowedBookBase):
    id: int
    book: BookResponse
    reader: ReaderResponse
    user: UserResponse

    class Config:
        orm_mode = True
