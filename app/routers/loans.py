from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, UserRole, LoanStatus
from app.schemas import LoanCreate, LoanResponse, MessageResponse
from app.crud import books as book_crud
from app.crud import users as user_crud
from app.crud import loans as loan_crud
from app.security import get_current_active_user, get_current_librarian

router = APIRouter(prefix="/loans", tags=["Loans & Returns"])


def _build_response(loan, db) -> LoanResponse:
    resp = LoanResponse.model_validate(loan)
    resp.book_title = loan.book.title if loan.book else None
    resp.user_name = loan.user.name if loan.user else None
    return resp


@router.post(
    "/borrow",
    response_model=LoanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Borrow a book",
    description=(
        "Creates a new loan for the **authenticated user** (or a target user if a "
        "Librarian specifies `user_id`). "
        "Enforces Limkokwing borrow limits, fine suspension, and availability checks."
    ),
)
def borrow_book(
    loan_in: LoanCreate,
    user_id: Optional[str] = Query(None, description="Target user ID (Librarian only)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # Librarians can borrow on behalf of any user
    if user_id and current_user.role != UserRole.LIBRARIAN:
        raise HTTPException(status_code=403, detail="Only Librarians can borrow on behalf of another user.")
    target = user_crud.get_user(db, user_id) if user_id else current_user
    if not target:
        raise HTTPException(status_code=404, detail=f"User '{user_id}' not found.")

    book = book_crud.get_book(db, loan_in.book_isbn)
    if not book:
        raise HTTPException(status_code=404, detail=f"Book ISBN '{loan_in.book_isbn}' not found.")

    try:
        loan = loan_crud.borrow_book(db, target, book)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    return _build_response(loan, db)


@router.post(
    "/return/{loan_id}",
    response_model=LoanResponse,
    summary="Return a borrowed book",
    description=(
        "Marks loan as **Returned** and computes the final fine (if overdue). "
        "Students/Staff can only return their own loans; Librarians can return any loan."
    ),
)
def return_book(
    loan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    loan = loan_crud.get_loan(db, loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail=f"Loan #{loan_id} not found.")

    if current_user.role != UserRole.LIBRARIAN and loan.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only return your own loans.")

    borrower = user_crud.get_user(db, loan.user_id)
    try:
        returned = loan_crud.return_book(db, loan, borrower)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    return _build_response(returned, db)


@router.get(
    "/",
    response_model=list[LoanResponse],
    summary="List loans",
    description="Librarians see all loans. Students/Staff see only their own.",
)
def list_loans(
    loan_status: Optional[LoanStatus] = Query(None, alias="status"),
    user_id: Optional[str] = Query(None, description="Filter by user (Librarian only)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role == UserRole.LIBRARIAN:
        target_id = user_id  # can be None (all) or specific
    else:
        target_id = current_user.id  # non-librarians always see own

    loans = loan_crud.get_loans(db, user_id=target_id, status=loan_status,
                                skip=skip, limit=limit)
    return [_build_response(l, db) for l in loans]


@router.get(
    "/{loan_id}",
    response_model=LoanResponse,
    summary="Get a specific loan by ID",
)
def get_loan(
    loan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    loan = loan_crud.get_loan(db, loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail=f"Loan #{loan_id} not found.")
    if current_user.role != UserRole.LIBRARIAN and loan.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied.")
    return _build_response(loan, db)


@router.post(
    "/sync-overdue",
    response_model=MessageResponse,
    summary="Sync overdue loan statuses [Librarian only]",
    description="Scans all BORROWED loans and marks past-due ones as OVERDUE.",
)
def sync_overdue(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_librarian),
):
    count = loan_crud.sync_overdue_statuses(db)
    return MessageResponse(
        message=f"Overdue sync complete.",
        detail=f"{count} loan(s) updated to OVERDUE status.",
    )
