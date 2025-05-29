from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import schemas as s
from app.crud import crud_readers as crud
from app.database import get_db
from app.models import User
from app.auth import get_current_user

router = APIRouter(prefix="/readers", tags=["readers"])


# вспомогательная функция
# обработка пустого возврата
def check_empty(readers):
    if not readers:
        raise HTTPException(
            status_code=404,
            detail=(
                "Readers not found" if isinstance(readers, list) else "Reader not found"
            ),
        )
    return readers


# получить список читателей
@router.get("/", response_model=list[s.ReaderResponse])
def read_readers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    readers = crud.get_all_readers(db, skip=skip, limit=limit)
    return check_empty(readers)


# получить читателя по ID
@router.get("/{reader_id}", response_model=s.ReaderResponse)
def get_reader(
    reader_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reader = crud.get_reader(db, reader_id)
    return check_empty(reader)


# создать читателя
@router.post("/", response_model=s.ReaderResponse, status_code=201)
def create_reader(
    reader: s.ReaderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_reader = crud.create_reader(db, reader)
    if not db_reader:
        raise HTTPException(status_code=400, detail="Failed to create reader")


# обновить читателя
@router.put("/{reader_id}", response_model=s.ReaderResponse)
def update_reader(
    reader_id: int,
    reader_data: s.ReaderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    updated_reader = crud.update_reader(db, reader_id, reader_data)
    return check_empty(updated_reader)


# удалить читателя
@router.delete("/{reader_id}", status_code=204)
def delete_reader(
    reader_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    success = crud.delete_reader(db, reader_id)
    if not success:
        raise HTTPException(status_code=404, detail="Reader not found")
    return {"message": "Reader deleted successfully"}
