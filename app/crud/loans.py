from datetime import date, timedelta
from typing import Optional
from sqlalchemy.orm import Session

from app.models import Book, Loan, LoanStatus, User, UserRole, BORROW_RULES


def _calculate_fine(loan: Loan, as_of: date) -> float:
    """Compute the current fine for an active/overdue loan."""
    if loan.status == LoanStatus.RETURNED:
        return loan.fine_amount
    if as_of <= loan.due_date:
        return 0.0
    overdue_days = (as_of - loan.due_date).days
    # Look up the user's fine rate
    from app.crud.users import get_user
    return 0.0  # placeholder — computed below with role


def calculate_fine_for_loan(loan: Loan, role: UserRole, as_of: Optional[date] = None) -> float:
    """Return fine amount (RM) for a given loan based on user role."""
    as_of = as_of or date.today()
    if loan.return_date:
        reference = loan.return_date
    else:
        reference = as_of

    if reference <= loan.due_date:
        return 0.0

    overdue_days = (reference - loan.due_date).days
    fine_per_day = BORROW_RULES[role]["fine_per_day"]
    return round(overdue_days * fine_per_day, 2)


def get_active_loans_count(db: Session, user_id: str) -> int:
    return (
        db.query(Loan)
        .filter(
            Loan.user_id == user_id,
            Loan.status.in_([LoanStatus.BORROWED, LoanStatus.OVERDUE]),
        )
        .count()
    )


def get_outstanding_fine_total(db: Session, user: User) -> float:
    loans = (
        db.query(Loan)
        .filter(
            Loan.user_id == user.id,
            Loan.status.in_([LoanStatus.BORROWED, LoanStatus.OVERDUE]),
        )
        .all()
    )
    today = date.today()
    total = sum(calculate_fine_for_loan(l, user.role, today) for l in loans)
    return round(total, 2)


def get_loan(db: Session, loan_id: int) -> Optional[Loan]:
    return db.query(Loan).filter(Loan.id == loan_id).first()


def get_loans(
    db: Session,
    user_id: Optional[str] = None,
    status: Optional[LoanStatus] = None,
    skip: int = 0,
    limit: int = 50,
) -> list[Loan]:
    q = db.query(Loan)
    if user_id:
        q = q.filter(Loan.user_id == user_id)
    if status:
        q = q.filter(Loan.status == status)
    return q.order_by(Loan.id.desc()).offset(skip).limit(limit).all()


def borrow_book(db: Session, user: User, book: Book) -> Loan:
    """
    Apply Limkokwing library rules, then create a Loan record.
    Raises ValueError with a descriptive message on rule violations.
    """
    rules = BORROW_RULES[user.role]

    # 1. Check borrow limit
    active_count = get_active_loans_count(db, user.id)
    if active_count >= rules["max_books"]:
        raise ValueError(
            f"Borrow limit reached. {user.role.value}s may hold at most "
            f"{rules['max_books']} book(s) at a time. "
            f"You currently have {active_count} active loan(s)."
        )

    # 2. Check outstanding fine block
    outstanding = get_outstanding_fine_total(db, user)
    block_threshold = rules["max_fine_before_block"]
    if outstanding >= block_threshold:
        raise ValueError(
            f"Your account is blocked due to outstanding fines of RM {outstanding:.2f}. "
            f"Please settle fines exceeding RM {block_threshold:.2f} at the library counter."
        )

    # 3. Check book availability
    if book.available_copies < 1:
        raise ValueError(
            f"'{book.title}' is currently unavailable. "
            "Please reserve it and you will be notified when a copy is returned."
        )

    # 4. Check for duplicate active loan of same book
    existing = (
        db.query(Loan)
        .filter(
            Loan.user_id == user.id,
            Loan.book_isbn == book.isbn,
            Loan.status.in_([LoanStatus.BORROWED, LoanStatus.OVERDUE]),
        )
        .first()
    )
    if existing:
        raise ValueError(
            f"You already have an active loan for '{book.title}' (Loan #{existing.id})."
        )

    # 5. Create loan
    today = date.today()
    due = today + timedelta(days=rules["loan_days"])
    loan = Loan(
        user_id=user.id,
        book_isbn=book.isbn,
        borrow_date=today,
        due_date=due,
        status=LoanStatus.BORROWED,
        fine_amount=0.0,
    )
    book.available_copies -= 1
    db.add(loan)
    db.commit()
    db.refresh(loan)
    return loan


def return_book(db: Session, loan: Loan, user: User) -> Loan:
    """
    Mark a loan as returned, compute and persist the final fine.
    """
    if loan.status == LoanStatus.RETURNED:
        raise ValueError(f"Loan #{loan.id} has already been returned.")

    today = date.today()
    fine = calculate_fine_for_loan(loan, user.role, today)

    loan.return_date = today
    loan.fine_amount = fine
    loan.status = LoanStatus.RETURNED

    # Restore book availability
    book = db.query(Book).filter(Book.isbn == loan.book_isbn).first()
    if book:
        book.available_copies = min(book.available_copies + 1, book.total_copies)

    db.commit()
    db.refresh(loan)
    return loan


def sync_overdue_statuses(db: Session) -> int:
    """Update BORROWED loans that are past due_date to OVERDUE. Returns count updated."""
    today = date.today()
    loans = (
        db.query(Loan)
        .filter(Loan.status == LoanStatus.BORROWED, Loan.due_date < today)
        .all()
    )
    for loan in loans:
        loan.status = LoanStatus.OVERDUE
    db.commit()
    return len(loans)
