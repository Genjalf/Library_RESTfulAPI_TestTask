from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas as s
from app.crud import crud_books as crud
from app.database import get_db
from app.auth import get_current_user
from app.models import User

router = APIRouter(prefix="/books", tags=["books"])


# вспомогательная функция
# обработка пустого возврата
def check_empty(books):
    if not books:
        raise HTTPException(
            status_code=404,
            detail="Books not found" if isinstance(books, list) else "Book not found",
        )
    return books


# создать новую книгу
@router.post("/", response_model=s.BookResponse, status_code=201)
def create_book(
    book: s.BookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.create_book(db, book)


# получить список книг
@router.get("/", response_model=list[s.BookResponse])
def read_books(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    books = crud.get_all_books(db, skip=skip, limit=limit)
    return check_empty(books)


# получить книгу по ID
@router.get("/{book_id}", response_model=s.BookResponse)
def read_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    book = crud.get_book(db, book_id)
    return check_empty(book)


# обновить книгу
@router.put("/{book_id}", response_model=s.BookResponse)
def update_book(
    book_id: int,
    book_data: s.BookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    updated_book = crud.update_book(db, book_id, book_data)
    return check_empty(updated_book)


# удалить книгу
# возвращает удаленную книгу
@router.delete("/{book_id}", response_model=s.BookResponse)
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted_book = crud.delete_book(db, book_id)
    return check_empty(deleted_book)
