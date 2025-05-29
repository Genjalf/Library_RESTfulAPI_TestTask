from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app import schemas as s
from app.crud import crud_borrowed_books as crud
from app.models import User

router = APIRouter(prefix="/borrow", tags=["borrow"])


# выдача книги
@router.post("/", response_model=s.BorrowedBookResponse, status_code=201)
def borrow_book(
    book_id: int,
    reader_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.issue_book(
        db=db, book_id=book_id, reader_id=reader_id, user_id=current_user.id
    )


# возврат книги
@router.put("/return", response_model=s.BorrowedBookResponse)
def return_borrowed_book(
    data: s.ReturnBookRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.return_book(
        db=db, reader_id=data.reader_id, book_id=data.book_id, bbook_id=data.bbook_id
    )


# получить все выданные книги
@router.get("/", response_model=list[s.BorrowedBookResponse])
def get_all_borrowed_books(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.get_all_borrowed_books(db, skip=skip, limit=limit)


# получить выданную книгу по ID
@router.get("/{borrowed_book_id}", response_model=s.BorrowedBookResponse)
def get_borrowed_book(
    borrowed_book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    borrowed_book = crud.get_borrowed_book(db, borrowed_book_id)
    if not borrowed_book:
        raise HTTPException(status_code=404, detail="Borrowed book not found")
    return borrowed_book


# обновить выданную книгу
@router.put("/{borrowed_book_id}", response_model=s.BorrowedBookResponse)
def update_borrowed_book(
    borrowed_book_id: int,
    borrowed_book_data: s.BorrowedBookUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    updated_borrowed_book = crud.update_borrowed_book(
        db, borrowed_book_id, borrowed_book_data
    )

    if not updated_borrowed_book:
        raise HTTPException(status_code=404, detail="Borrowed book not found")

    return updated_borrowed_book


# удалить выданную книгу
@router.delete("/{borrowed_book_id}", response_model=s.BorrowedBookResponse)
def delete_borrowed_book(
    borrowed_book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    borrowed_book = crud.get_borrowed_book(db, borrowed_book_id)
    if not borrowed_book:
        raise HTTPException(status_code=404, detail="Borrowed book not found")

    # проверяем, возвращена ли книга, чтобы не удалить запись о невозвращенной книге
    if borrowed_book.return_date is None:
        raise HTTPException(status_code=400, detail="Borrowed book not returned yet")

    deleted_borrowed_book = crud.delete_borrowed_book(db, borrowed_book_id)
    if not deleted_borrowed_book:
        raise HTTPException(status_code=500, detail="Failed to delete borrowed book")
    return deleted_borrowed_book


# Получить все книги, выданные читателю в данный момент
@router.get("/reader/{reader_id}/unreturn", response_model=list[s.BorrowedBookResponse])
def get_borrowed_books_by_reader(
    reader_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    borrowed_books = crud.get_unreturned_books_by_reader(db, reader_id)
    if not borrowed_books:
        raise HTTPException(
            status_code=404, detail="No borrowed books found for this reader"
        )
    return borrowed_books


# Получить все книги, когда либо выданные читателю
@router.get("/reader/{reader_id}/all", response_model=list[s.BorrowedBookResponse])
def get_all_borrowed_books_by_reader(
    reader_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    borrowed_books = crud.get_all_borrowed_books_by_reader(db, reader_id)

    if not borrowed_books:
        raise HTTPException(
            status_code=404, detail="No borrowed books found for this reader"
        )
    return borrowed_books
