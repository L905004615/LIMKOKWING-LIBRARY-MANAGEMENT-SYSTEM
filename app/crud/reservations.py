from datetime import date
from typing import Optional
from sqlalchemy.orm import Session

from app.models import Book, Reservation, ReservationStatus, User


def get_reservation(db: Session, reservation_id: int) -> Optional[Reservation]:
    return db.query(Reservation).filter(Reservation.id == reservation_id).first()


def get_reservations(
    db: Session,
    user_id: Optional[str] = None,
    status: Optional[ReservationStatus] = None,
    book_isbn: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
) -> list[Reservation]:
    q = db.query(Reservation)
    if user_id:
        q = q.filter(Reservation.user_id == user_id)
    if status:
        q = q.filter(Reservation.status == status)
    if book_isbn:
        q = q.filter(Reservation.book_isbn == book_isbn)
    return q.order_by(Reservation.id.desc()).offset(skip).limit(limit).all()


def create_reservation(db: Session, user: User, book: Book) -> Reservation:
    """
    Reserve a book. Rules:
    - Cannot reserve a book that is currently available (borrow it instead).
    - Cannot have duplicate pending reservation for the same book.
    """
    if book.available_copies > 0:
        raise ValueError(
            f"'{book.title}' is currently available. "
            "Please borrow it directly instead of reserving."
        )

    existing = (
        db.query(Reservation)
        .filter(
            Reservation.user_id == user.id,
            Reservation.book_isbn == book.isbn,
            Reservation.status == ReservationStatus.PENDING,
        )
        .first()
    )
    if existing:
        raise ValueError(
            f"You already have a pending reservation for '{book.title}' "
            f"(Reservation #{existing.id})."
        )

    reservation = Reservation(
        user_id=user.id,
        book_isbn=book.isbn,
        reservation_date=date.today(),
        status=ReservationStatus.PENDING,
    )
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation


def cancel_reservation(db: Session, reservation: Reservation) -> Reservation:
    if reservation.status != ReservationStatus.PENDING:
        raise ValueError(
            f"Reservation #{reservation.id} cannot be cancelled "
            f"(current status: {reservation.status.value})."
        )
    reservation.status = ReservationStatus.CANCELLED
    db.commit()
    db.refresh(reservation)
    return reservation


def fulfil_reservation(db: Session, reservation: Reservation) -> Reservation:
    """Called by librarian when a reserved book becomes available."""
    if reservation.status != ReservationStatus.PENDING:
        raise ValueError(
            f"Reservation #{reservation.id} is not in Pending state."
        )
    reservation.status = ReservationStatus.FULFILLED
    db.commit()
    db.refresh(reservation)
    return reservation
