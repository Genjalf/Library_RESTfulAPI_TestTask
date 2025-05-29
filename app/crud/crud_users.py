from sqlalchemy.orm import Session
from app import models as m, schemas as s
from app.auth import hash_password
from typing import Optional


# создание библиотекаря
def create_user(db: Session, user: s.UserCreate) -> Optional[m.User]:
    # проверям не создан ли уже такой библиотекарь
    db_user = db.query(m.User).filter(m.User.email == user.email).first()
    if db_user:
        return None  # если библиотекарь уже есть, возвращаем None

    # создаем библиотекаря
    db_user = m.User(email=user.email, hashed_password=hash_password(user.password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
