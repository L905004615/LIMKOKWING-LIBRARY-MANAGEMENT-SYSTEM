from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, UserRole, ReservationStatus
from app.schemas import ReservationCreate, ReservationResponse, MessageResponse
from app.crud import books as book_crud
from app.crud import reservations as res_crud
from app.security import get_current_active_user, get_current_librarian

router = APIRouter(prefix="/reservations", tags=["Reservations"])


def _build_response(res, db) -> ReservationResponse:
    resp = ReservationResponse.model_validate(res)
    resp.book_title = res.book.title if res.book else None
    resp.user_name = res.user.name if res.user else None
    return resp


@router.post(
    "/",
    response_model=ReservationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Reserve a book",
    description=(
        "Reserve a book that is **currently on loan** (all copies borrowed). "
        "If the book has available copies, borrow it directly."
    ),
)
def create_reservation(
    res_in: ReservationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    book = book_crud.get_book(db, res_in.book_isbn)
    if not book:
        raise HTTPException(status_code=404, detail=f"Book ISBN '{res_in.book_isbn}' not found.")
    try:
        reservation = res_crud.create_reservation(db, current_user, book)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    return _build_response(reservation, db)


@router.delete(
    "/{reservation_id}/cancel",
    response_model=ReservationResponse,
    summary="Cancel a pending reservation",
)
def cancel_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    res = res_crud.get_reservation(db, reservation_id)
    if not res:
        raise HTTPException(status_code=404, detail=f"Reservation #{reservation_id} not found.")
    if current_user.role != UserRole.LIBRARIAN and res.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only cancel your own reservations.")
    try:
        cancelled = res_crud.cancel_reservation(db, res)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return _build_response(cancelled, db)


@router.post(
    "/{reservation_id}/fulfil",
    response_model=ReservationResponse,
    summary="Mark a reservation as fulfilled [Librarian only]",
    description="Called when a reserved book becomes available and is handed to the member.",
)
def fulfil_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_librarian),
):
    res = res_crud.get_reservation(db, reservation_id)
    if not res:
        raise HTTPException(status_code=404, detail=f"Reservation #{reservation_id} not found.")
    try:
        fulfilled = res_crud.fulfil_reservation(db, res)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return _build_response(fulfilled, db)


@router.get(
    "/",
    response_model=list[ReservationResponse],
    summary="List reservations",
    description="Librarians see all. Students/Staff see only their own.",
)
def list_reservations(
    res_status: Optional[ReservationStatus] = Query(None, alias="status"),
    book_isbn: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None, description="Filter by user (Librarian only)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    target_id = user_id if current_user.role == UserRole.LIBRARIAN else current_user.id
    reservations = res_crud.get_reservations(
        db, user_id=target_id, status=res_status,
        book_isbn=book_isbn, skip=skip, limit=limit,
    )
    return [_build_response(r, db) for r in reservations]


@router.get(
    "/{reservation_id}",
    response_model=ReservationResponse,
    summary="Get a specific reservation",
)
def get_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    res = res_crud.get_reservation(db, reservation_id)
    if not res:
        raise HTTPException(status_code=404, detail=f"Reservation #{reservation_id} not found.")
    if current_user.role != UserRole.LIBRARIAN and res.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied.")
    return _build_response(res, db)
