# Limkokwing University Library Management System
## Technical Project Documentation

**Version:** 1.0.0
**Date:** June 2026
**Technology:** Python · FastAPI · SQLAlchemy · SQLite · JWT
**Author:** Limkokwing University IT Department

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Project Structure](#3-project-structure)
4. [Database Design](#4-database-design)
5. [Business Rules & Library Policy](#5-business-rules--library-policy)
6. [Authentication & Security](#6-authentication--security)
7. [API Reference](#7-api-reference)
8. [Module Documentation](#8-module-documentation)
9. [Installation & Setup](#9-installation--setup)
10. [Configuration](#10-configuration)
11. [Data Seeding](#11-data-seeding)
12. [Error Handling](#12-error-handling)
13. [Dependencies](#13-dependencies)

---

## 1. Project Overview

The **Limkokwing University Library Management System (LLMS)** is a RESTful backend API built with Python's **FastAPI** framework. It provides a complete digital management solution for the Limkokwing University library, handling:

- Book catalog management (add, update, search, delete)
- Member management (students, staff, librarians)
- Book borrowing and returning with automatic fine calculation
- Book reservation system for unavailable titles
- Role-based access control (Librarian, Student, Staff)
- JWT-based authentication

The system is **backend-only** — it exposes a fully documented REST API accessible via the built-in interactive Swagger UI at `/docs`.

### Key Features

| Feature | Description |
|---------|-------------|
| JWT Authentication | Stateless, secure Bearer token login |
| Role-Based Access | Three roles: Librarian, Student, Staff |
| Smart Fine Calculation | Automatic overdue fine calculation per user role |
| Borrow Limit Enforcement | Different limits per role; blocks users with high fines |
| Book Reservation | Reserve books that are currently on loan |
| Full-Text Search | Search books by title, author, or ISBN |
| Auto Swagger Docs | Interactive API docs at `/docs` |

---

## 2. System Architecture

```
┌──────────────────────────────────────────────────────┐
│               CLIENT (Swagger UI / HTTP)              │
└──────────────────────┬───────────────────────────────┘
                       │ HTTP Requests
                       ▼
┌──────────────────────────────────────────────────────┐
│                   FastAPI App (main.py)               │
│  ┌─────────────────────────────────────────────────┐ │
│  │              Middleware (CORS)                   │ │
│  └─────────────────────────────────────────────────┘ │
│  ┌────────────┐ ┌────────┐ ┌───────┐ ┌───────────┐  │
│  │ /auth      │ │/books  │ │/users │ │  /loans   │  │
│  │ Router     │ │Router  │ │Router │ │  Router   │  │
│  └────────────┘ └────────┘ └───────┘ └───────────┘  │
│         ┌─────────────────────────────┐              │
│         │       /reservations          │              │
│         │          Router             │              │
│         └─────────────────────────────┘              │
│  ┌─────────────────────────────────────────────────┐ │
│  │            Security Layer (JWT + Roles)          │ │
│  └─────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────┐ │
│  │              CRUD Layer                          │ │
│  │  users.py | books.py | loans.py | reservations  │ │
│  └─────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────┐ │
│  │           SQLAlchemy ORM (models.py)             │ │
│  └─────────────────────────────────────────────────┘ │
└──────────────────────┬───────────────────────────────┘
                       │
                       ▼
         ┌─────────────────────────┐
         │   SQLite Database       │
         │     (library.db)        │
         └─────────────────────────┘
```

### Request Flow

```
HTTP Request
    → CORS Middleware
    → FastAPI Router (matches path & method)
    → Security Dependency (JWT validation → load User)
    → Role Dependency (check role permissions)
    → Endpoint Handler
    → CRUD function (business logic)
    → SQLAlchemy (database query/write)
    → Pydantic Schema (serialize response)
    → HTTP Response (JSON)
```

---

## 3. Project Structure

```
LIMKOKWING-LIBRARY-MANAGEMENT-SYSTEM/
│
├── app/                            # Main application package
│   ├── __init__.py                 # Package marker
│   ├── main.py                     # FastAPI app entry point, router registration
│   ├── database.py                 # SQLAlchemy engine, session, Base class
│   ├── models.py                   # ORM models + business rule constants
│   ├── schemas.py                  # Pydantic v2 request/response schemas
│   ├── security.py                 # JWT, password hashing, auth dependencies
│   │
│   ├── crud/                       # Database operation layer
│   │   ├── __init__.py
│   │   ├── users.py                # User CRUD + authentication
│   │   ├── books.py                # Book CRUD + search
│   │   ├── loans.py                # Borrow/return + fine logic (core business)
│   │   └── reservations.py         # Reservation management
│   │
│   └── routers/                    # HTTP route handlers
│       ├── __init__.py
│       ├── auth.py                 # POST /auth/login, /auth/register, GET /auth/me
│       ├── books.py                # CRUD for /books/
│       ├── users.py                # CRUD for /users/
│       ├── loans.py                # Borrow/return for /loans/
│       └── reservations.py         # CRUD for /reservations/
│
├── venv/                           # Python virtual environment (not committed)
├── library.db                      # SQLite database file (auto-created)
├── requirements.txt                # Python package dependencies
├── seed.py                         # Database seeder script
├── verify.py                       # End-to-end API test script
├── README.md                       # Quick-start guide
├── PROJECT_DOCUMENTATION.md        # This file (technical reference)
└── USER_MANUAL.md                  # End-user guide
```

---

## 4. Database Design

The system uses **SQLite** via **SQLAlchemy ORM**. The database file `library.db` is automatically created in the project root on first startup.

### Entity Relationship Diagram

```
┌───────────────────┐         ┌───────────────────────┐
│       User        │         │         Book           │
├───────────────────┤         ├───────────────────────┤
│ id (PK) VARCHAR   │         │ isbn (PK) VARCHAR      │
│ name VARCHAR      │         │ title VARCHAR          │
│ email VARCHAR UQ  │         │ author VARCHAR         │
│ hashed_password   │         │ publisher VARCHAR      │
│ role ENUM         │         │ year_published INT     │
│ is_active BOOL    │         │ category VARCHAR       │
│ created_at DATE   │         │ total_copies INT       │
└────────┬──────────┘         │ available_copies INT   │
         │                    │ location VARCHAR       │
         │                    │ description VARCHAR    │
         │                    └──────────┬────────────┘
         │                               │
         │   ┌─────────────────────┐     │
         └───┤       Loan          ├─────┘
             ├─────────────────────┤
             │ id (PK) INT AI      │
             │ user_id (FK)        │
             │ book_isbn (FK)      │
             │ borrow_date DATE    │
             │ due_date DATE       │
             │ return_date DATE    │
             │ fine_amount FLOAT   │
             │ status ENUM         │
             └─────────────────────┘

         ┌─────────────────────────┐
         │      Reservation        │
         ├─────────────────────────┤
         │ id (PK) INT AI          │
         │ user_id (FK → User)     │
         │ book_isbn (FK → Book)   │
         │ reservation_date DATE   │
         │ status ENUM             │
         └─────────────────────────┘
```

### Table Definitions

#### `users`
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | VARCHAR(20) | PRIMARY KEY | Student/Staff ID (e.g. `LU905004615`) |
| `name` | VARCHAR(100) | NOT NULL | Full name |
| `email` | VARCHAR(150) | UNIQUE, NOT NULL | University email |
| `hashed_password` | VARCHAR(255) | NOT NULL | bcrypt hash |
| `role` | ENUM | NOT NULL | `Librarian`, `Student`, `Staff` |
| `is_active` | BOOLEAN | DEFAULT TRUE | Account status |
| `created_at` | DATETIME | DEFAULT NOW | Registration timestamp |

#### `books`
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `isbn` | VARCHAR(17) | PRIMARY KEY | ISBN-10 or ISBN-13 |
| `title` | VARCHAR(255) | NOT NULL | Book title |
| `author` | VARCHAR(150) | NOT NULL | Author name(s) |
| `publisher` | VARCHAR(150) | NOT NULL | Publisher |
| `year_published` | INTEGER | NOT NULL | Publication year |
| `category` | VARCHAR(100) | NOT NULL | Limkokwing faculty category |
| `total_copies` | INTEGER | DEFAULT 1 | Total physical copies |
| `available_copies` | INTEGER | DEFAULT 1 | Currently available for borrowing |
| `location` | VARCHAR(100) | DEFAULT 'Main Library' | Shelf location |
| `description` | VARCHAR(500) | NULLABLE | Optional synopsis |

#### `loans`
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Loan ID |
| `user_id` | VARCHAR(20) | FK → users.id | Borrower |
| `book_isbn` | VARCHAR(17) | FK → books.isbn | Borrowed book |
| `borrow_date` | DATE | NOT NULL | Date borrowed |
| `due_date` | DATE | NOT NULL | Return deadline |
| `return_date` | DATE | NULLABLE | Actual return date |
| `fine_amount` | FLOAT | DEFAULT 0.0 | Final fine in RM |
| `status` | ENUM | NOT NULL | `Borrowed`, `Returned`, `Overdue` |

#### `reservations`
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Reservation ID |
| `user_id` | VARCHAR(20) | FK → users.id | Member who reserved |
| `book_isbn` | VARCHAR(17) | FK → books.isbn | Reserved book |
| `reservation_date` | DATE | NOT NULL | Date of reservation |
| `status` | ENUM | NOT NULL | `Pending`, `Fulfilled`, `Cancelled` |

---

## 5. Business Rules & Library Policy

### Borrowing Limits by Role

| Rule | Student | Staff | Librarian |
|------|---------|-------|-----------|
| Max books at once | **3** | **5** | **10** |
| Loan duration | **14 days** | **30 days** | **60 days** |
| Fine per overdue day | **RM 0.50** | **RM 0.20** | **RM 0.00** |
| Fine suspension threshold | **RM 10.00** | **RM 10.00** | N/A |

### Rule Enforcement (enforced in `app/crud/loans.py`)

1. **Borrow Limit Check** — Before creating a loan, the system counts the user's active loans (status `Borrowed` or `Overdue`). If at or above the role limit, the borrow is rejected.

2. **Fine Suspension Check** — The system calculates the user's current outstanding fines across all active loans. If the total meets or exceeds RM 10.00, borrowing is blocked until fines are settled at the library counter.

3. **Availability Check** — `available_copies` must be > 0. On borrow, it is decremented by 1. On return, it is incremented by 1 (capped at `total_copies`).

4. **Duplicate Loan Check** — A user cannot borrow the same book twice if they already have an active loan for it.

5. **Fine Calculation Formula:**
   ```
   overdue_days = return_date (or today) - due_date
   fine = overdue_days × fine_per_day (by role)
   ```
   Fine is only calculated if the book is past its due date. No fine for on-time returns.

### Reservation Rules

- A book **can only be reserved** when `available_copies == 0`. If copies are available, the user must borrow it directly.
- A user cannot have two `Pending` reservations for the same book.
- Reservations can be `Cancelled` by the user or librarian.
- Librarians mark reservations as `Fulfilled` when the book is handed to the member.

### Book Categories (Limkokwing Faculty Aligned)

```
Creative Multimedia
Computing & IT
Design Innovation
Architecture & Built Environment
Business & Globalization
Fashion & Textile
Music & Sound Production
Film & Television
General Reference
Periodicals & Journals
```

---

## 6. Authentication & Security

### JWT (JSON Web Token)

- **Algorithm:** `HS256`
- **Token Lifetime:** 8 hours (480 minutes)
- **Secret Key:** Configured in `app/security.py` → `SECRET_KEY` (change in production)
- **Token Format:** `Bearer <token>` in the `Authorization` HTTP header

### Password Hashing

- Library: `passlib` with `bcrypt` backend (version 4.0.1)
- Passwords are **never stored in plain text**
- Verification uses `passlib.context.CryptContext`

### Role Dependencies (FastAPI `Depends`)

| Dependency | Description |
|-----------|-------------|
| `get_current_user` | Validates JWT, loads User from DB |
| `get_current_active_user` | Extends above; rejects deactivated accounts |
| `get_current_librarian` | Extends above; rejects non-Librarian roles |

### Login Flow

```
POST /auth/login
  Body: username=<user_id>&password=<password>  (form data)
  ↓
  authenticate_user() → verify password hash
  ↓
  create_access_token({"sub": user_id})
  ↓
  Returns: { access_token, token_type, user_id, name, role }
```

---

## 7. API Reference

**Base URL:** `http://127.0.0.1:8000`
**Auth:** Bearer token via `Authorization: Bearer <token>` header

### Authentication Endpoints

| Method | Path | Auth Required | Role | Description |
|--------|------|---------------|------|-------------|
| `POST` | `/auth/register` | No | — | Register new member |
| `POST` | `/auth/login` | No | — | Login, get JWT token |
| `GET` | `/auth/me` | Yes | Any | View own profile |

#### POST /auth/register
```json
Request Body:
{
  "id": "LU905004615",
  "name": "Lamarana Sow",
  "email": "lamarana@student.limkokwing.edu.my",
  "password": "mypassword",
  "role": "Student"
}

Response 201:
{
  "id": "LU905004615",
  "name": "Lamarana Sow",
  "email": "lamarana@student.limkokwing.edu.my",
  "role": "Student",
  "is_active": true,
  "created_at": "2026-06-07T12:00:00",
  "active_loans_count": 0,
  "total_outstanding_fine": 0.0
}
```

#### POST /auth/login
```
Content-Type: application/x-www-form-urlencoded
Body: username=LU905004615&password=mypassword

Response 200:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5...",
  "token_type": "bearer",
  "user_id": "LU905004615",
  "name": "Lamarana Sow",
  "role": "Student"
}
```

---

### Book Endpoints

| Method | Path | Auth | Role | Description |
|--------|------|------|------|-------------|
| `GET` | `/books/` | Yes | Any | Search/list catalog |
| `GET` | `/books/categories` | Yes | Any | List categories |
| `GET` | `/books/{isbn}` | Yes | Any | Get book details |
| `POST` | `/books/` | Yes | Librarian | Add new book |
| `PATCH` | `/books/{isbn}` | Yes | Librarian | Update book |
| `DELETE` | `/books/{isbn}` | Yes | Librarian | Remove book |

#### Query Parameters for GET /books/
| Param | Type | Description |
|-------|------|-------------|
| `search` | string | Search title, author, or ISBN |
| `category` | string | Filter by category |
| `available_only` | boolean | Only show books in stock |
| `skip` | int | Pagination offset (default 0) |
| `limit` | int | Results per page (default 20, max 100) |

---

### User Endpoints

| Method | Path | Auth | Role | Description |
|--------|------|------|------|-------------|
| `GET` | `/users/` | Yes | Librarian | List all members |
| `POST` | `/users/` | Yes | Librarian | Create member account |
| `GET` | `/users/fines` | Yes | Librarian | Users with outstanding fines |
| `GET` | `/users/{id}` | Yes | Self / Librarian | Get profile |
| `PATCH` | `/users/{id}` | Yes | Librarian | Update profile |
| `DELETE` | `/users/{id}` | Yes | Librarian | Delete member |

---

### Loan Endpoints

| Method | Path | Auth | Role | Description |
|--------|------|------|------|-------------|
| `POST` | `/loans/borrow` | Yes | Any | Borrow a book |
| `POST` | `/loans/return/{id}` | Yes | Any (scoped) | Return a book |
| `GET` | `/loans/` | Yes | Any (scoped) | List loans |
| `GET` | `/loans/{id}` | Yes | Any (scoped) | Loan details |
| `POST` | `/loans/sync-overdue` | Yes | Librarian | Mark overdue loans |

#### POST /loans/borrow
```json
Request Body:
{ "book_isbn": "978-0-13-468599-1" }

Optional Query: ?user_id=LU905004615  (Librarian only)

Response 201:
{
  "id": 1,
  "user_id": "LU905004615",
  "book_isbn": "978-0-13-468599-1",
  "borrow_date": "2026-06-07",
  "due_date": "2026-06-21",
  "return_date": null,
  "fine_amount": 0.0,
  "status": "Borrowed",
  "book_title": "Computer Science: An Overview",
  "user_name": "Lamarana Sow"
}
```

---

### Reservation Endpoints

| Method | Path | Auth | Role | Description |
|--------|------|------|------|-------------|
| `POST` | `/reservations/` | Yes | Any | Reserve a book |
| `DELETE` | `/reservations/{id}/cancel` | Yes | Any (scoped) | Cancel reservation |
| `POST` | `/reservations/{id}/fulfil` | Yes | Librarian | Fulfil reservation |
| `GET` | `/reservations/` | Yes | Any (scoped) | List reservations |
| `GET` | `/reservations/{id}` | Yes | Any (scoped) | Reservation details |

---

### Standard Error Responses

| HTTP Code | When |
|-----------|------|
| `400` | Malformed request |
| `401` | Missing or invalid JWT token |
| `403` | Insufficient role permissions / account inactive |
| `404` | Resource not found |
| `409` | Conflict (duplicate ID, email, active loan, etc.) |
| `422` | Business rule violation (borrow limit, fine block, unavailable) |

---

## 8. Module Documentation

### `app/main.py`
- Creates the `FastAPI` application with full metadata (title, description, version)
- Uses `lifespan` context manager to call `Base.metadata.create_all()` on startup
- Registers CORS middleware (open in dev; restrict in production)
- Includes all 5 routers: `auth`, `books`, `users`, `loans`, `reservations`
- Exposes `GET /` health check endpoint

### `app/database.py`
- Creates SQLite engine with `check_same_thread=False` for FastAPI's async handling
- Defines `SessionLocal` factory via `sessionmaker`
- Defines `Base` class via `DeclarativeBase` (SQLAlchemy 2.x style)
- Provides `get_db()` generator dependency for request-scoped DB sessions

### `app/models.py`
- Defines all 4 SQLAlchemy models: `User`, `Book`, `Loan`, `Reservation`
- Uses Python `enum.Enum` for `UserRole`, `LoanStatus`, `ReservationStatus`
- Defines `BORROW_RULES` dict — the single source of truth for all policy values
- Defines `BOOK_CATEGORIES` list used in validation

### `app/schemas.py`
- All Pydantic v2 (`BaseModel`) request and response schemas
- Uses `model_config = {"from_attributes": True}` for ORM compatibility
- `BookCreate.validate_category()` — field validator enforcing allowed categories
- `UserResponse` includes computed fields: `active_loans_count`, `total_outstanding_fine`

### `app/security.py`
- `get_password_hash(password)` — bcrypt hash via passlib
- `verify_password(plain, hashed)` — constant-time comparison
- `create_access_token(data, expires_delta)` — creates signed JWT
- `decode_access_token(token)` — decodes and validates JWT, returns `user_id` or `None`
- FastAPI dependencies: `get_current_user`, `get_current_active_user`, `get_current_librarian`

### `app/crud/loans.py` *(Core business logic)*
- `calculate_fine_for_loan(loan, role, as_of)` — computes fine in RM
- `get_active_loans_count(db, user_id)` — counts Borrowed + Overdue loans
- `get_outstanding_fine_total(db, user)` — sums real-time fines for all active loans
- `borrow_book(db, user, book)` — enforces all 4 borrow rules, creates Loan record
- `return_book(db, loan, user)` — closes loan, calculates final fine, restores availability
- `sync_overdue_statuses(db)` — batch updates BORROWED → OVERDUE for past-due loans

---

## 9. Installation & Setup

### Prerequisites
- Python 3.10 or higher
- `pip` package manager
- Windows PowerShell (or any terminal)

### Step-by-Step Setup

```powershell
# Step 1: Navigate to project folder
cd C:\Users\DELL\Desktop\LIMKOKWING-LIBRARY-MANAGEMENT-SYSTEM

# Step 2: Allow PowerShell scripts (one-time)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Step 3: Create virtual environment
C:\Users\DELL\AppData\Local\Programs\Python\Python313\python.exe -m venv venv

# Step 4: Activate virtual environment
.\venv\Scripts\Activate.ps1
# Prompt changes to (venv) PS ...>

# Step 5: Install dependencies
pip install -r requirements.txt

# Step 6: Seed the database
python seed.py

# Step 7: Start the server
uvicorn app.main:app --reload
```

### Verify Installation
Open your browser and go to: **http://127.0.0.1:8000/docs**

---

## 10. Configuration

All configuration is in `app/security.py`. For production deployment, these should be moved to environment variables (`.env` file with `python-dotenv`):

| Setting | Current Value | Description |
|---------|--------------|-------------|
| `SECRET_KEY` | `limkokwing-library-super-secret-key-...` | JWT signing key — **change in production!** |
| `ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `480` (8 hours) | Token validity duration |

Database URL is in `app/database.py`:
```python
DATABASE_URL = "sqlite:///./library.db"
```
To switch to PostgreSQL, change this to:
```python
DATABASE_URL = "postgresql://user:password@localhost/librarydb"
```
and install `psycopg2-binary`.

---

## 11. Data Seeding

The `seed.py` script pre-populates the database with realistic sample data. It is **idempotent** — running it multiple times will not create duplicates.

### Seeded Users (6 accounts)
| ID | Name | Role | Password |
|----|------|------|----------|
| LIB001 | Fatimah Hassan | Librarian | librarian123 |
| LU905004615 | Lamarana Sow | Student | student123 |
| LU905012345 | Ahmad bin Ali | Student | student123 |
| LU905098765 | Siti Nora binti Yusof | Student | student123 |
| LUS9876 | Dr. Rajesh Kumar | Staff | staff123 |
| LUS1234 | Ms. Aileen Tan | Staff | staff123 |

### Seeded Books (15 titles across 8 categories)
| Category | Count |
|----------|-------|
| Computing & IT | 4 |
| Creative Multimedia | 2 |
| Design Innovation | 2 |
| Architecture & Built Environment | 1 |
| Business & Globalization | 2 |
| Fashion & Textile | 1 |
| Music & Sound Production | 1 |
| Film & Television | 1 |
| General Reference | 1 |

---

## 12. Error Handling

The system uses FastAPI's `HTTPException` for all errors. Business rule violations (borrow limit, fine block, unavailability) return **HTTP 422** with a descriptive `detail` message.

### Example Error Responses

**Borrow Limit Exceeded (422)**
```json
{
  "detail": "Borrow limit reached. Students may hold at most 3 book(s) at a time. You currently have 3 active loan(s)."
}
```

**Fine Suspension (422)**
```json
{
  "detail": "Your account is blocked due to outstanding fines of RM 10.50. Please settle fines exceeding RM 10.00 at the library counter."
}
```

**Book Not Available (422)**
```json
{
  "detail": "'Computer Science: An Overview' is currently unavailable. Please reserve it and you will be notified when a copy is returned."
}
```

**Unauthorized (401)**
```json
{
  "detail": "Could not validate credentials. Please log in again."
}
```

---

## 13. Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `fastapi` | 0.115.5 | Web framework |
| `uvicorn[standard]` | 0.32.1 | ASGI server with hot-reload |
| `sqlalchemy` | 2.0.36 | ORM and database toolkit |
| `pydantic[email]` | 2.10.3 | Data validation and serialization |
| `pyjwt` | 2.10.1 | JWT token encoding/decoding |
| `cryptography` | 44.0.0 | Cryptographic backend for PyJWT |
| `passlib[bcrypt]` | 1.7.4 | Password hashing |
| `bcrypt` | 4.0.1 | bcrypt backend (passlib compatible) |
| `python-multipart` | 0.0.20 | OAuth2 form data parsing |
| `python-dateutil` | 2.9.0 | Date utilities |

---

*End of Technical Documentation*
