from datetime import datetime, date
from typing import Optional
from sqlalchemy import String, Integer, Float, Boolean, Date, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.database import Base


class UserRole(str, enum.Enum):
    LIBRARIAN = "Librarian"
    STUDENT = "Student"
    STAFF = "Staff"


class LoanStatus(str, enum.Enum):
    BORROWED = "Borrowed"
    RETURNED = "Returned"
    OVERDUE = "Overdue"


class ReservationStatus(str, enum.Enum):
    PENDING = "Pending"
    FULFILLED = "Fulfilled"
    CANCELLED = "Cancelled"


# ──────────────────────────────────────────────────────────
# Borrowing Rules (Limkokwing Library Policy)
# ──────────────────────────────────────────────────────────
BORROW_RULES = {
    UserRole.STUDENT: {
        "max_books": 3,
        "loan_days": 14,
        "fine_per_day": 0.50,
        "max_fine_before_block": 10.00,
    },
    UserRole.STAFF: {
        "max_books": 5,
        "loan_days": 30,
        "fine_per_day": 0.20,
        "max_fine_before_block": 10.00,
    },
    UserRole.LIBRARIAN: {
        "max_books": 10,
        "loan_days": 60,
        "fine_per_day": 0.00,
        "max_fine_before_block": 9999.00,
    },
}

BOOK_CATEGORIES = [
    "Creative Multimedia",
    "Computing & IT",
    "Design Innovation",
    "Architecture & Built Environment",
    "Business & Globalization",
    "Fashion & Textile",
    "Music & Sound Production",
    "Film & Television",
    "General Reference",
    "Periodicals & Journals",
]


# ──────────────────────────────────────────────────────────
# Models
# ──────────────────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(20), primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), default=UserRole.STUDENT)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    loans: Mapped[list["Loan"]] = relationship("Loan", back_populates="user")
    reservations: Mapped[list["Reservation"]] = relationship("Reservation", back_populates="user")


class Book(Base):
    __tablename__ = "books"

    isbn: Mapped[str] = mapped_column(String(17), primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    author: Mapped[str] = mapped_column(String(150))
    publisher: Mapped[str] = mapped_column(String(150))
    year_published: Mapped[int] = mapped_column(Integer)
    category: Mapped[str] = mapped_column(String(100))
    total_copies: Mapped[int] = mapped_column(Integer, default=1)
    available_copies: Mapped[int] = mapped_column(Integer, default=1)
    location: Mapped[str] = mapped_column(String(100), default="Main Library")
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    loans: Mapped[list["Loan"]] = relationship("Loan", back_populates="book")
    reservations: Mapped[list["Reservation"]] = relationship("Reservation", back_populates="book")


class Loan(Base):
    __tablename__ = "loans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(20), ForeignKey("users.id"))
    book_isbn: Mapped[str] = mapped_column(String(17), ForeignKey("books.isbn"))
    borrow_date: Mapped[date] = mapped_column(Date)
    due_date: Mapped[date] = mapped_column(Date)
    return_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    fine_amount: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[LoanStatus] = mapped_column(SAEnum(LoanStatus), default=LoanStatus.BORROWED)

    user: Mapped["User"] = relationship("User", back_populates="loans")
    book: Mapped["Book"] = relationship("Book", back_populates="loans")


class Reservation(Base):
    __tablename__ = "reservations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(20), ForeignKey("users.id"))
    book_isbn: Mapped[str] = mapped_column(String(17), ForeignKey("books.isbn"))
    reservation_date: Mapped[date] = mapped_column(Date)
    status: Mapped[ReservationStatus] = mapped_column(
        SAEnum(ReservationStatus), default=ReservationStatus.PENDING
    )

    user: Mapped["User"] = relationship("User", back_populates="reservations")
    book: Mapped["Book"] = relationship("Book", back_populates="reservations")
