from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models import UserRole, LoanStatus, ReservationStatus, BOOK_CATEGORIES


# ──────────────────────────────────────────────────────────
# Auth / Token Schemas
# ──────────────────────────────────────────────────────────
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    name: str
    role: UserRole


class TokenData(BaseModel):
    user_id: Optional[str] = None


# ──────────────────────────────────────────────────────────
# User Schemas
# ──────────────────────────────────────────────────────────
class UserCreate(BaseModel):
    id: str = Field(..., min_length=3, max_length=20, examples=["LU905004615"])
    name: str = Field(..., min_length=2, max_length=100, examples=["Ahmad bin Ali"])
    email: EmailStr = Field(..., examples=["ahmad@limkokwing.edu.my"])
    password: str = Field(..., min_length=6, examples=["securepassword"])
    role: UserRole = UserRole.STUDENT


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime
    active_loans_count: int = 0
    total_outstanding_fine: float = 0.0

    model_config = {"from_attributes": True}


class UserSummary(BaseModel):
    id: str
    name: str
    role: UserRole
    is_active: bool

    model_config = {"from_attributes": True}


# ──────────────────────────────────────────────────────────
# Book Schemas
# ──────────────────────────────────────────────────────────
class BookCreate(BaseModel):
    isbn: str = Field(..., min_length=10, max_length=17, examples=["978-967-5080-12-3"])
    title: str = Field(..., min_length=1, max_length=255, examples=["Digital Design Fundamentals"])
    author: str = Field(..., min_length=1, max_length=150, examples=["Kenneth Bahr"])
    publisher: str = Field(..., min_length=1, max_length=150, examples=["Limkokwing Press"])
    year_published: int = Field(..., ge=1900, le=2100, examples=[2023])
    category: str = Field(..., examples=["Computing & IT"])
    total_copies: int = Field(1, ge=1, le=100)
    location: str = Field("Main Library", examples=["Level 2, Aisle B"])
    description: Optional[str] = Field(None, max_length=500)

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        if v not in BOOK_CATEGORIES:
            raise ValueError(
                f"Category must be one of: {', '.join(BOOK_CATEGORIES)}"
            )
        return v


class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    author: Optional[str] = Field(None, max_length=150)
    publisher: Optional[str] = Field(None, max_length=150)
    year_published: Optional[int] = Field(None, ge=1900, le=2100)
    category: Optional[str] = None
    total_copies: Optional[int] = Field(None, ge=1, le=100)
    location: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in BOOK_CATEGORIES:
            raise ValueError(
                f"Category must be one of: {', '.join(BOOK_CATEGORIES)}"
            )
        return v


class BookResponse(BaseModel):
    isbn: str
    title: str
    author: str
    publisher: str
    year_published: int
    category: str
    total_copies: int
    available_copies: int
    location: str
    description: Optional[str]

    model_config = {"from_attributes": True}


# ──────────────────────────────────────────────────────────
# Loan Schemas
# ──────────────────────────────────────────────────────────
class LoanCreate(BaseModel):
    book_isbn: str = Field(..., examples=["978-967-5080-12-3"])


class LoanResponse(BaseModel):
    id: int
    user_id: str
    book_isbn: str
    borrow_date: date
    due_date: date
    return_date: Optional[date]
    fine_amount: float
    status: LoanStatus
    book_title: Optional[str] = None
    user_name: Optional[str] = None

    model_config = {"from_attributes": True}


# ──────────────────────────────────────────────────────────
# Reservation Schemas
# ──────────────────────────────────────────────────────────
class ReservationCreate(BaseModel):
    book_isbn: str = Field(..., examples=["978-967-5080-12-3"])


class ReservationResponse(BaseModel):
    id: int
    user_id: str
    book_isbn: str
    reservation_date: date
    status: ReservationStatus
    book_title: Optional[str] = None
    user_name: Optional[str] = None

    model_config = {"from_attributes": True}


# ──────────────────────────────────────────────────────────
# General Schemas
# ──────────────────────────────────────────────────────────
class MessageResponse(BaseModel):
    message: str
    detail: Optional[str] = None


class FineResponse(BaseModel):
    user_id: str
    user_name: str
    total_outstanding_fine: float
    loans_with_fines: list[LoanResponse]
