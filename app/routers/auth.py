from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import Token, UserCreate, UserResponse, MessageResponse
from app.crud import users as user_crud
from app.security import create_access_token, get_current_active_user
from app.models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new library member",
    description=(
        "Create a new account. **User ID** should follow the Limkokwing student/staff "
        "number format (e.g. `LU905004615` for students, `LUS9876` for staff). "
        "Role defaults to `Student`."
    ),
)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    if user_crud.get_user(db, user_in.id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User ID '{user_in.id}' is already registered.",
        )
    if user_crud.get_user_by_email(db, user_in.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Email '{user_in.email}' is already in use.",
        )
    user = user_crud.create_user(db, user_in)
    response = UserResponse.model_validate(user)
    response.active_loans_count = 0
    response.total_outstanding_fine = 0.0
    return response


@router.post(
    "/login",
    response_model=Token,
    summary="Login to obtain a JWT access token",
    description=(
        "Submit your **User ID** as `username` and your **password**. "
        "The returned `access_token` (Bearer) must be included in the "
        "`Authorization` header for all protected endpoints."
    ),
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = user_crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect User ID or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is deactivated. Contact the librarian.",
        )
    token = create_access_token({"sub": user.id})
    return Token(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        name=user.name,
        role=user.role,
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get your own profile",
)
def read_me(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    from app.crud.loans import get_active_loans_count, get_outstanding_fine_total

    response = UserResponse.model_validate(current_user)
    response.active_loans_count = get_active_loans_count(db, current_user.id)
    response.total_outstanding_fine = get_outstanding_fine_total(db, current_user)
    return response
