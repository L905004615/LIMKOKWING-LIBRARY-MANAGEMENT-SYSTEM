from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, BOOK_CATEGORIES
from app.schemas import BookCreate, BookResponse, BookUpdate, MessageResponse
from app.crud import books as book_crud
from app.security import get_current_active_user, get_current_librarian

router = APIRouter(prefix="/books", tags=["Books"])


@router.get(
    "/",
    response_model=list[BookResponse],
    summary="List / search books in the catalog",
    description=(
        "Supports full-text search across **title**, **author**, and **ISBN**. "
        "Optionally filter by **category** or show only **available** copies. "
        "Accessible by all authenticated users."
    ),
)
def list_books(
    search: Optional[str] = Query(None, description="Search by title, author, or ISBN"),
    category: Optional[str] = Query(None, description="Filter by category"),
    available_only: bool = Query(False, description="Show only books with available copies"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    return book_crud.get_books(db, skip=skip, limit=limit, search=search,
                               category=category, available_only=available_only)


@router.get(
    "/categories",
    response_model=list[str],
    summary="List all Limkokwing library categories",
)
def list_categories(_: User = Depends(get_current_active_user)):
    return BOOK_CATEGORIES


@router.get(
    "/{isbn}",
    response_model=BookResponse,
    summary="Get a single book by ISBN",
)
def get_book(
    isbn: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    book = book_crud.get_book(db, isbn)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Book with ISBN '{isbn}' not found.")
    return book


@router.post(
    "/",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new book to the catalog [Librarian only]",
)
def create_book(
    book_in: BookCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_librarian),
):
    if book_crud.get_book(db, book_in.isbn):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A book with ISBN '{book_in.isbn}' already exists. "
                   "Use PATCH to update copies.",
        )
    return book_crud.create_book(db, book_in)


@router.patch(
    "/{isbn}",
    response_model=BookResponse,
    summary="Update book details [Librarian only]",
)
def update_book(
    isbn: str,
    book_in: BookUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_librarian),
):
    book = book_crud.get_book(db, isbn)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Book with ISBN '{isbn}' not found.")
    return book_crud.update_book(db, book, book_in)


@router.delete(
    "/{isbn}",
    response_model=MessageResponse,
    summary="Remove a book from the catalog [Librarian only]",
)
def delete_book(
    isbn: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_librarian),
):
    book = book_crud.get_book(db, isbn)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Book with ISBN '{isbn}' not found.")
    if book.available_copies < book.total_copies:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot delete '{book.title}': {book.total_copies - book.available_copies} "
                   "copy/copies are currently on loan.",
        )
    book_crud.delete_book(db, book)
    return MessageResponse(message=f"Book '{book.title}' (ISBN: {isbn}) has been removed.")
