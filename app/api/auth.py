from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas as s
from app.crud import crud_users as crud
from app.database import get_db
from app.models import User
from app.auth import pwd_context, create_access_token

router = APIRouter()


# эндпоинт для регистрации библиотекаря
@router.post("/register", response_model=s.UserResponse)
def register_user(user: s.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.create_user(db=db, user=user)
    if db_user is None:
        raise HTTPException(status_code=400, detail="User already exists")
    return s.UserResponse(id=db_user.id, email=db_user.email)


# эндпоинт для логина
@router.post("/login")
def login(user: s.UserLogin, db: Session = Depends(get_db)) -> dict:
    # ищем по email
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user is None:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # проверяем пароль
    if not pwd_context.verify(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # создаем и отправляем токен
    access_token = create_access_token(data={"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}
