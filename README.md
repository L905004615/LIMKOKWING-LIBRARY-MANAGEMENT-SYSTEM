# Limkokwing University Library Management System

A **Python FastAPI** backend for managing Limkokwing University's library — books, loans, reservations, users, and fines.

---

## 🚀 Quick Setup

### 1. Prerequisites
- Python 3.10+ (found at `C:\Users\DELL\AppData\Local\Programs\Python\Python313\python.exe`)

### 2. Create a Virtual Environment
```powershell
# In the project root:
C:\Users\DELL\AppData\Local\Programs\Python\Python313\python.exe -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Seed the Database
```powershell
python seed.py
```
This creates `library.db` (SQLite) and populates sample users and books.

### 5. Run the Server
```powershell
uvicorn app.main:app --reload
```

### 6. Open the API Docs
| Interface | URL |
|-----------|-----|
| **Swagger UI** (interactive) | http://127.0.0.1:8000/docs |
| **ReDoc** (reference) | http://127.0.0.1:8000/redoc |

---

## 🔑 Default Credentials

| Role | User ID | Password |
|------|---------|----------|
| **Librarian** | `LIB001` | `librarian123` |
| **Student** | `LU905004615` | `student123` |
| **Staff** | `LUS9876` | `staff123` |

---

## 📚 Library Rules (Limkokwing Policy)

| Role | Max Books | Loan Period | Fine/Day | Fine Block Threshold |
|------|-----------|-------------|----------|----------------------|
| **Student** | 3 | 14 days | RM 0.50 | RM 10.00 |
| **Staff** | 5 | 30 days | RM 0.20 | RM 10.00 |
| **Librarian** | 10 | 60 days | RM 0.00 | N/A |

---

## 🗂 Project Structure

```
LIMKOKWING-LIBRARY-MANAGEMENT-SYSTEM/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── database.py          # SQLite connection & session
│   ├── models.py            # SQLAlchemy ORM models
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── security.py          # JWT auth & role dependencies
│   ├── crud/
│   │   ├── users.py         # User CRUD & auth
│   │   ├── books.py         # Book CRUD & search
│   │   ├── loans.py         # Borrow/return & fine logic
│   │   └── reservations.py  # Reservation management
│   └── routers/
│       ├── auth.py          # /auth/login, /auth/register, /auth/me
│       ├── books.py         # /books/
│       ├── users.py         # /users/
│       ├── loans.py         # /loans/
│       └── reservations.py  # /reservations/
├── seed.py                  # Database seeder
├── requirements.txt         # Python dependencies
└── library.db               # SQLite database (auto-created)
```

---

## 🔐 Authentication Flow

1. **Login**: `POST /auth/login` with `username` (User ID) + `password`
2. **Authorize**: Copy the `access_token` → click **Authorize 🔒** in Swagger → paste as `Bearer <token>`
3. **Use endpoints**: All protected routes now work with your role

---

## 📡 API Endpoints Summary

### Auth
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | `/auth/register` | Public | Register a new member |
| POST | `/auth/login` | Public | Login → get JWT token |
| GET | `/auth/me` | All | View your own profile |

### Books
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/books/` | All | Search & list catalog |
| GET | `/books/categories` | All | List all categories |
| GET | `/books/{isbn}` | All | Get book details |
| POST | `/books/` | Librarian | Add new book |
| PATCH | `/books/{isbn}` | Librarian | Update book details |
| DELETE | `/books/{isbn}` | Librarian | Remove book |

### Users
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/users/` | Librarian | List all members |
| POST | `/users/` | Librarian | Create user account |
| GET | `/users/fines` | Librarian | Users with outstanding fines |
| GET | `/users/{id}` | Self/Librarian | Get user profile |
| PATCH | `/users/{id}` | Librarian | Update user |
| DELETE | `/users/{id}` | Librarian | Delete user |

### Loans
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | `/loans/borrow` | All | Borrow a book |
| POST | `/loans/return/{id}` | All | Return a book |
| GET | `/loans/` | All (scoped) | List loans |
| GET | `/loans/{id}` | All (scoped) | Loan details |
| POST | `/loans/sync-overdue` | Librarian | Mark overdue loans |

### Reservations
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | `/reservations/` | All | Reserve a book |
| DELETE | `/reservations/{id}/cancel` | All (scoped) | Cancel reservation |
| POST | `/reservations/{id}/fulfil` | Librarian | Mark reservation fulfilled |
| GET | `/reservations/` | All (scoped) | List reservations |
| GET | `/reservations/{id}` | All (scoped) | Reservation details |
