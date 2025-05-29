from fastapi import FastAPI
from app.api import auth, books, readers, borrow

app = FastAPI()

app.include_router(auth.router)
app.include_router(books.router)
app.include_router(readers.router)
app.include_router(borrow.router)
