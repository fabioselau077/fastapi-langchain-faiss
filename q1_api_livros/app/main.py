from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy.orm import Session

from . import crud, schemas
from .database import Base, engine, get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Biblioteca Virtual",
    description="API para cadastro e consulta de livros.",
    version="1.0.0",
    lifespan=lifespan,
)

DbSession = Annotated[Session, Depends(get_db)]


@app.post(
    "/books",
    response_model=schemas.BookRead,
    status_code=status.HTTP_201_CREATED,
    tags=["livros"],
    summary="Cadastra um livro",
)
def create_book(book: schemas.BookCreate, db: DbSession):
    """Cadastra um novo livro e retorna o registro com o id gerado."""
    return crud.create_book(db, book)


@app.get(
    "/books",
    response_model=list[schemas.BookRead],
    tags=["livros"],
    summary="Busca livros por título ou autor",
)
def list_books(
    db: DbSession,
    title: Annotated[str | None, Query(description="Trecho do título")] = None,
    author: Annotated[str | None, Query(description="Trecho do nome do autor")] = None,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
):
    """
    Busca parcial e sem diferenciar maiúsculas de minúsculas.
    Os filtros podem ser combinados; sem nenhum filtro, lista todos os livros.
    """
    return crud.search_books(db, title=title, author=author, skip=skip, limit=limit)


@app.get(
    "/books/{book_id}",
    response_model=schemas.BookRead,
    tags=["livros"],
    summary="Detalha um livro",
)
def get_book(book_id: int, db: DbSession):
    book = crud.get_book(db, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    return book