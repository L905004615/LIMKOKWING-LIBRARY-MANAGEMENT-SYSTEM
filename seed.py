"""
seed.py — Populate the Limkokwing Library database with sample data.
Run once after setting up the project:

    python seed.py
"""

from app.database import SessionLocal, engine
from app.models import Base, User, Book, UserRole
from app.security import get_password_hash
from datetime import datetime

# ──────────────────────────────────────────────────────────
# Sample Users
# ──────────────────────────────────────────────────────────
USERS = [
    {
        "id": "LIB001",
        "name": "Fatimah Hassan",
        "email": "fatimah.hassan@limkokwing.edu.my",
        "password": "librarian123",
        "role": UserRole.LIBRARIAN,
    },
    {
        "id": "LU905004615",
        "name": "Lamarana Sow",
        "email": "lamarana.sow@student.limkokwing.edu.my",
        "password": "student123",
        "role": UserRole.STUDENT,
    },
    {
        "id": "LU905012345",
        "name": "Ahmad bin Ali",
        "email": "ahmad.ali@student.limkokwing.edu.my",
        "password": "student123",
        "role": UserRole.STUDENT,
    },
    {
        "id": "LU905098765",
        "name": "Siti Nora binti Yusof",
        "email": "siti.nora@student.limkokwing.edu.my",
        "password": "student123",
        "role": UserRole.STUDENT,
    },
    {
        "id": "LUS9876",
        "name": "Dr. Rajesh Kumar",
        "email": "rajesh.kumar@limkokwing.edu.my",
        "password": "staff123",
        "role": UserRole.STAFF,
    },
    {
        "id": "LUS1234",
        "name": "Ms. Aileen Tan",
        "email": "aileen.tan@limkokwing.edu.my",
        "password": "staff123",
        "role": UserRole.STAFF,
    },
]

# ──────────────────────────────────────────────────────────
# Sample Books (Limkokwing-relevant catalog)
# ──────────────────────────────────────────────────────────
BOOKS = [
    {
        "isbn": "978-0-13-468599-1",
        "title": "Computer Science: An Overview",
        "author": "Glenn Brookshear",
        "publisher": "Pearson",
        "year_published": 2019,
        "category": "Computing & IT",
        "total_copies": 5,
        "location": "Level 2, Aisle A",
        "description": "A comprehensive introduction to computer science fundamentals.",
    },
    {
        "isbn": "978-0-13-110163-0",
        "title": "The C Programming Language",
        "author": "Brian W. Kernighan & Dennis M. Ritchie",
        "publisher": "Prentice Hall",
        "year_published": 1988,
        "category": "Computing & IT",
        "total_copies": 3,
        "location": "Level 2, Aisle A",
        "description": "The definitive guide to the C programming language.",
    },
    {
        "isbn": "978-0-596-51774-8",
        "title": "Learning Python",
        "author": "Mark Lutz",
        "publisher": "O'Reilly Media",
        "year_published": 2013,
        "category": "Computing & IT",
        "total_copies": 4,
        "location": "Level 2, Aisle B",
        "description": "Comprehensive guide to the Python programming language.",
    },
    {
        "isbn": "978-0-321-12521-7",
        "title": "Domain-Driven Design",
        "author": "Eric Evans",
        "publisher": "Addison-Wesley",
        "year_published": 2003,
        "category": "Computing & IT",
        "total_copies": 2,
        "location": "Level 2, Aisle B",
        "description": "Tackling complexity in the heart of software.",
    },
    {
        "isbn": "978-0-321-48521-5",
        "title": "Multimedia: Making It Work",
        "author": "Tay Vaughan",
        "publisher": "McGraw-Hill",
        "year_published": 2011,
        "category": "Creative Multimedia",
        "total_copies": 6,
        "location": "Level 1, Aisle C",
        "description": "Practical guide to multimedia production.",
    },
    {
        "isbn": "978-1-119-28897-7",
        "title": "The Principles of Beautiful Web Design",
        "author": "Jason Beaird & James George",
        "publisher": "SitePoint",
        "year_published": 2020,
        "category": "Design Innovation",
        "total_copies": 4,
        "location": "Level 1, Aisle D",
        "description": "A practical guide to designing stunning websites.",
    },
    {
        "isbn": "978-0-470-08964-3",
        "title": "Graphic Design: The New Basics",
        "author": "Ellen Lupton & Jennifer Cole Phillips",
        "publisher": "Princeton Architectural Press",
        "year_published": 2015,
        "category": "Design Innovation",
        "total_copies": 3,
        "location": "Level 1, Aisle D",
        "description": "Fundamental principles of graphic design for the digital age.",
    },
    {
        "isbn": "978-0-13-235088-4",
        "title": "Architecture: Form, Space, and Order",
        "author": "Francis D.K. Ching",
        "publisher": "Wiley",
        "year_published": 2014,
        "category": "Architecture & Built Environment",
        "total_copies": 4,
        "location": "Level 3, Aisle E",
        "description": "A classic visual reference on architectural form and design.",
    },
    {
        "isbn": "978-0-470-53178-5",
        "title": "Principles of Corporate Finance",
        "author": "Richard Brealey, Stewart Myers & Franklin Allen",
        "publisher": "McGraw-Hill",
        "year_published": 2022,
        "category": "Business & Globalization",
        "total_copies": 5,
        "location": "Level 3, Aisle F",
        "description": "The gold standard text on corporate finance.",
    },
    {
        "isbn": "978-0-13-611205-2",
        "title": "Marketing Management",
        "author": "Philip Kotler & Kevin Lane Keller",
        "publisher": "Pearson",
        "year_published": 2022,
        "category": "Business & Globalization",
        "total_copies": 4,
        "location": "Level 3, Aisle F",
        "description": "The authoritative guide to marketing strategy and practice.",
    },
    {
        "isbn": "978-0-500-51774-3",
        "title": "Fashion Design Course",
        "author": "Steven Faerm",
        "publisher": "Thames & Hudson",
        "year_published": 2017,
        "category": "Fashion & Textile",
        "total_copies": 3,
        "location": "Level 1, Aisle G",
        "description": "Principles, practice and techniques for the aspiring fashion designer.",
    },
    {
        "isbn": "978-0-240-81602-5",
        "title": "Sound Design: The Expressive Power of Music, Voice and Sound Effects in Cinema",
        "author": "David Sonnenschein",
        "publisher": "Michael Wiese Productions",
        "year_published": 2001,
        "category": "Music & Sound Production",
        "total_copies": 2,
        "location": "Level 1, Aisle H",
        "description": "A comprehensive guide to sound design for film.",
    },
    {
        "isbn": "978-0-240-80690-3",
        "title": "Cinematography: Theory and Practice",
        "author": "Blain Brown",
        "publisher": "Focal Press",
        "year_published": 2011,
        "category": "Film & Television",
        "total_copies": 3,
        "location": "Level 1, Aisle H",
        "description": "Imagemaking for cinematographers, directors, and videographers.",
    },
    {
        "isbn": "978-0-19-853188-0",
        "title": "Oxford Dictionary of Computing",
        "author": "Oxford University Press",
        "publisher": "Oxford University Press",
        "year_published": 2008,
        "category": "General Reference",
        "total_copies": 2,
        "location": "Level 2, Reference Section",
        "description": "A comprehensive dictionary of computing terms.",
    },
    {
        "isbn": "978-0-521-89365-8",
        "title": "The Art and Science of Digital Compositing",
        "author": "Ron Brinkmann",
        "publisher": "Morgan Kaufmann",
        "year_published": 2008,
        "category": "Creative Multimedia",
        "total_copies": 2,
        "location": "Level 1, Aisle C",
        "description": "Techniques for digital compositing in film and video.",
    },
]


def seed():
    print("[*] Starting database seeding...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Seed users
        users_added = 0
        for u in USERS:
            existing = db.query(User).filter(User.id == u["id"]).first()
            if not existing:
                db.add(User(
                    id=u["id"],
                    name=u["name"],
                    email=u["email"],
                    hashed_password=get_password_hash(u["password"]),
                    role=u["role"],
                    is_active=True,
                    created_at=datetime.utcnow(),
                ))
                users_added += 1
        db.commit()
        print(f"    [OK] Users seeded: {users_added} new account(s).")

        # Seed books
        books_added = 0
        for b in BOOKS:
            existing = db.query(Book).filter(Book.isbn == b["isbn"]).first()
            if not existing:
                db.add(Book(
                    isbn=b["isbn"],
                    title=b["title"],
                    author=b["author"],
                    publisher=b["publisher"],
                    year_published=b["year_published"],
                    category=b["category"],
                    total_copies=b["total_copies"],
                    available_copies=b["total_copies"],
                    location=b["location"],
                    description=b.get("description"),
                ))
                books_added += 1
        db.commit()
        print(f"    [OK] Books seeded: {books_added} new title(s).")

        print("\n[DONE] Seeding complete!")
        print("\nDefault Login Credentials:")
        print("   +-------------+------------------+----------------+")
        print("   | Role        | User ID          | Password       |")
        print("   +-------------+------------------+----------------+")
        print("   | Librarian   | LIB001           | librarian123   |")
        print("   | Student     | LU905004615      | student123     |")
        print("   | Staff       | LUS9876          | staff123       |")
        print("   +-------------+------------------+----------------+")
        print("\nStart the server:  uvicorn app.main:app --reload")
        print("Swagger UI:        http://127.0.0.1:8000/docs")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
