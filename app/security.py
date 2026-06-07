from datetime import datetime, timezone, timedelta
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, UserRole

# ──────────────────────────────────────────────────────────
# Configuration  (in production, load these from env vars)
# ──────────────────────────────────────────────────────────
SECRET_KEY = "limkokwing-library-super-secret-key-2024-do-not-share"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 hours

# ──────────────────────────────────────────────────────────
# Password Hashing
# ──────────────────────────────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# ──────────────────────────────────────────────────────────
# JWT Token Utilities
# ──────────────────────────────────────────────────────────
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[str]:
    """Returns user_id from token or None if invalid/expired."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: Optional[str] = payload.get("sub")
        return user_id
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


# ──────────────────────────────────────────────────────────
# FastAPI Dependencies
# ──────────────────────────────────────────────────────────
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials. Please log in again.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user_id = decode_access_token(token)
    if user_id is None:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated. Please contact the librarian.",
        )
    return current_user


def get_current_librarian(current_user: User = Depends(get_current_active_user)) -> User:
    if current_user.role != UserRole.LIBRARIAN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. This action requires Librarian privileges.",
        )
    return current_user


def get_librarian_or_self(
    user_id: str,
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Allow librarians full access, or users to access their own data."""
    if current_user.role != UserRole.LIBRARIAN and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own data.",
        )
    return current_user
