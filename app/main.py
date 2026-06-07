from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine
from app.models import Base
from app.routers import auth, books, users, loans, reservations


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all database tables on startup
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Limkokwing University Library Management System",
    description="""
## 📚 Limkokwing University Library API

A comprehensive library management backend for **Limkokwing University of Creative Technology**.

### Features
- **JWT Authentication** — Secure Bearer token login
- **Role-based access** — Librarian · Student · Staff
- **Book Catalog** — Full CRUD with search by title, author, ISBN and category filter
- **Loan Management** — Borrow & return with automatic fine calculation
- **Reservation System** — Reserve unavailable books
- **Fine Enforcement** — Automatic suspension when fines exceed RM 10.00

### Library Borrowing Rules
| Role | Max Books | Loan Duration | Fine / Day | Suspension Threshold |
|------|-----------|---------------|------------|----------------------|
| Student | 3 | 14 days | RM 0.50 | RM 10.00 |
| Staff | 5 | 30 days | RM 0.20 | RM 10.00 |
| Librarian | 10 | 60 days | RM 0.00 | N/A |

### Quick Start
1. Register or use the seeded accounts (see `seed.py`)
2. Login via `POST /auth/login` to get your token
3. Click **Authorize 🔒** above and paste your token
4. Explore all endpoints!

### Default Seeded Accounts
| Role | User ID | Password |
|------|---------|----------|
| Librarian | `LIB001` | `librarian123` |
| Student | `LU905004615` | `student123` |
| Staff | `LUS9876` | `staff123` |
    """,
    version="1.0.0",
    contact={
        "name": "Limkokwing Library Services",
        "email": "library@limkokwing.edu.my",
    },
    license_info={
        "name": "Academic Use Only",
    },
    lifespan=lifespan,
)

# CORS (open for development; tighten in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers
app.include_router(auth.router)
app.include_router(books.router)
app.include_router(users.router)
app.include_router(loans.router)
app.include_router(reservations.router)


@app.get("/", tags=["Health"], summary="API Health Check")
def root():
    return {
        "system": "Limkokwing University Library Management System",
        "status": "online",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }
