from typing import Optional
from sqlalchemy.orm import Session

from app.models import User, UserRole, Loan, LoanStatus
from app.schemas import UserCreate, UserUpdate
from app.security import get_password_hash


def get_user(db: Session, user_id: str) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_users(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    role: Optional[UserRole] = None,
    is_active: Optional[bool] = None,
) -> list[User]:
    q = db.query(User)
    if role:
        q = q.filter(User.role == role)
    if is_active is not None:
        q = q.filter(User.is_active == is_active)
    return q.offset(skip).limit(limit).all()


def create_user(db: Session, user_in: UserCreate) -> User:
    hashed = get_password_hash(user_in.password)
    db_user = User(
        id=user_in.id,
        name=user_in.name,
        email=user_in.email,
        hashed_password=hashed,
        role=user_in.role,
        is_active=True,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user: User, user_in: UserUpdate) -> User:
    for field, value in user_in.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user: User) -> None:
    db.delete(user)
    db.commit()


def get_user_outstanding_fine(db: Session, user_id: str) -> float:
    """Sum up fine_amount for all non-returned loans."""
    loans = (
        db.query(Loan)
        .filter(
            Loan.user_id == user_id,
            Loan.status.in_([LoanStatus.BORROWED, LoanStatus.OVERDUE]),
        )
        .all()
    )
    total = sum(loan.fine_amount for loan in loans)
    return round(total, 2)


def authenticate_user(db: Session, user_id: str, password: str) -> Optional[User]:
    from app.security import verify_password

    user = get_user(db, user_id)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
