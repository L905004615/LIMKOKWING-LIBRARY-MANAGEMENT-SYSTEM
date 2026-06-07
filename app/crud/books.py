from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models import Book
from app.schemas import BookCreate, BookUpdate


def get_book(db: Session, isbn: str) -> Optional[Book]:
    return db.query(Book).filter(Book.isbn == isbn).first()


def get_books(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    search: Optional[str] = None,
    category: Optional[str] = None,
    available_only: bool = False,
) -> list[Book]:
    q = db.query(Book)
    if search:
        term = f"%{search}%"
        q = q.filter(
            or_(
                Book.title.ilike(term),
                Book.author.ilike(term),
                Book.isbn.ilike(term),
            )
        )
    if category:
        q = q.filter(Book.category == category)
    if available_only:
        q = q.filter(Book.available_copies > 0)
    return q.offset(skip).limit(limit).all()


def create_book(db: Session, book_in: BookCreate) -> Book:
    db_book = Book(
        isbn=book_in.isbn,
        title=book_in.title,
        author=book_in.author,
        publisher=book_in.publisher,
        year_published=book_in.year_published,
        category=book_in.category,
        total_copies=book_in.total_copies,
        available_copies=book_in.total_copies,
        location=book_in.location,
        description=book_in.description,
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


def update_book(db: Session, book: Book, book_in: BookUpdate) -> Book:
    data = book_in.model_dump(exclude_unset=True)
    if "total_copies" in data:
        # Adjust available copies by the difference
        diff = data["total_copies"] - book.total_copies
        book.available_copies = max(0, book.available_copies + diff)
    for field, value in data.items():
        setattr(book, field, value)
    db.commit()
    db.refresh(book)
    return book


def delete_book(db: Session, book: Book) -> None:
    db.delete(book)
    db.commit()
