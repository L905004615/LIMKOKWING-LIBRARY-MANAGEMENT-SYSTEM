from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, UserRole
from app.schemas import UserCreate, UserResponse, UserUpdate, FineResponse, MessageResponse
from app.crud import users as user_crud
from app.crud.loans import get_active_loans_count, get_outstanding_fine_total, get_loans
from app.security import get_current_active_user, get_current_librarian

router = APIRouter(prefix="/users", tags=["Users"])


def _enrich(user: User, db: Session) -> UserResponse:
    resp = UserResponse.model_validate(user)
    resp.active_loans_count = get_active_loans_count(db, user.id)
    resp.total_outstanding_fine = get_outstanding_fine_total(db, user)
    return resp


# ── Librarian endpoints ────────────────────────────────────
@router.get(
    "/",
    response_model=list[UserResponse],
    summary="List all library members [Librarian only]",
)
def list_users(
    role: Optional[UserRole] = Query(None),
    is_active: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_librarian),
):
    users = user_crud.get_users(db, skip=skip, limit=limit, role=role, is_active=is_active)
    return [_enrich(u, db) for u in users]


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a user account [Librarian only]",
    description="Allows a librarian to register any role, including other Librarians.",
)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_librarian),
):
    if user_crud.get_user(db, user_in.id):
        raise HTTPException(status_code=409, detail=f"User ID '{user_in.id}' already exists.")
    if user_crud.get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=409, detail=f"Email '{user_in.email}' already in use.")
    user = user_crud.create_user(db, user_in)
    return _enrich(user, db)


@router.get(
    "/fines",
    response_model=list[FineResponse],
    summary="List all users with outstanding fines [Librarian only]",
)
def list_users_with_fines(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_librarian),
):
    from app.models import LoanStatus
    from app.crud.loans import calculate_fine_for_loan

    users = user_crud.get_users(db, limit=1000)
    result = []
    for user in users:
        loans_with_fines = []
        from app.models import Loan
        import datetime

        active_loans = (
            db.query(Loan)
            .filter(
                Loan.user_id == user.id,
                Loan.status.in_([LoanStatus.BORROWED, LoanStatus.OVERDUE]),
            )
            .all()
        )
        total = 0.0
        for loan in active_loans:
            fine = calculate_fine_for_loan(loan, user.role)
            if fine > 0:
                from app.schemas import LoanResponse
                lr = LoanResponse.model_validate(loan)
                lr.fine_amount = fine
                lr.book_title = loan.book.title if loan.book else None
                lr.user_name = user.name
                loans_with_fines.append(lr)
                total += fine
        if total > 0:
            result.append(
                FineResponse(
                    user_id=user.id,
                    user_name=user.name,
                    total_outstanding_fine=round(total, 2),
                    loans_with_fines=loans_with_fines,
                )
            )
    return result


# ── Per-user endpoints ─────────────────────────────────────
@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get a user's profile (self or librarian)",
)
def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != UserRole.LIBRARIAN and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied.")
    user = user_crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User '{user_id}' not found.")
    return _enrich(user, db)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update a user's profile [Librarian only]",
)
def update_user(
    user_id: str,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_librarian),
):
    user = user_crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User '{user_id}' not found.")
    if user_in.email and user_crud.get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=409, detail="Email already in use by another account.")
    updated = user_crud.update_user(db, user, user_in)
    return _enrich(updated, db)


@router.delete(
    "/{user_id}",
    response_model=MessageResponse,
    summary="Delete a user [Librarian only]",
)
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_librarian),
):
    user = user_crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User '{user_id}' not found.")
    active = get_active_loans_count(db, user_id)
    if active > 0:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot delete user with {active} active loan(s). "
                   "Ensure all books are returned first.",
        )
    user_crud.delete_user(db, user)
    return MessageResponse(message=f"User '{user_id}' has been removed from the system.")
