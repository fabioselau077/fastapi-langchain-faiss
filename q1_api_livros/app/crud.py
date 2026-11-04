from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models, schemas


def create_book(db: Session, data: schemas.BookCreate) -> models.Book:
    book = models.Book(**data.model_dump())
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


def get_book(db: Session, book_id: int) -> models.Book | None:
    return db.get(models.Book, book_id)


def search_books(
    db: Session,
    title: str | None = None,
    author: str | None = None,
    skip: int = 0,
    limit: int = 50,
) -> list[models.Book]:
    query = select(models.Book)

    # autoescape evita que % e _ digitados pelo user virem curinga no LIKE
    if title:
        query = query.where(models.Book.title.icontains(title, autoescape=True))
    if author:
        query = query.where(models.Book.author.icontains(author, autoescape=True))

    query = query.order_by(models.Book.title).offset(skip).limit(limit)
    return list(db.scalars(query))