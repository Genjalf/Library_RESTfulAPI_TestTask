from sqlalchemy.orm import Session
from app import models as m, schemas as s
from typing import Optional


# создание читателя
def create_reader(db: Session, reader: s.ReaderCreate) -> m.Reader:
    db_reader = m.Reader(name=reader.name, email=reader.email)
    db.add(db_reader)
    db.commit()
    db.refresh(db_reader)
    return db_reader


# получение всех читателей
def get_all_readers(db: Session, skip: int = 0, limit: int = 100) -> list[m.Reader]:
    return db.query(m.Reader).offset(skip).limit(limit).all()


# получение читателя по ID
def get_reader(db: Session, reader_id: int) -> Optional[m.Reader]:
    return db.query(m.Reader).filter(m.Reader.id == reader_id).first()


# обновление читателя
def update_reader(
    db: Session,
    reader_id: int,
    reader_data: s.ReaderUpdate,
) -> Optional[m.Reader]:

    db_reader = get_reader(db, reader_id)
    if not db_reader:
        return None
    for key, value in reader_data.dict().items():
        setattr(db_reader, key, value)
    db.commit()
    db.refresh(db_reader)
    return db_reader


# удаление читателя
def delete_reader(db: Session, reader_id: int) -> Optional[m.Reader]:
    db_reader = db.query(m.Reader).filter(m.Reader.id == reader_id).first()
    if not db_reader:
        return None
    db.delete(db_reader)
    db.commit()
    return db_reader
