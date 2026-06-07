# Limkokwing University Library Management System
## User Manual

**Version:** 1.0.0  
**Date:** June 2026  
**Prepared for:** Library Members — Students, Staff, and Librarians  
**System URL:** http://127.0.0.1:8000/docs

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Getting Started — How to Log In](#2-getting-started--how-to-log-in)
3. [Understanding Your Role](#3-understanding-your-role)
4. [Student Guide](#4-student-guide)
   - 4.1 View Your Profile
   - 4.2 Search for Books
   - 4.3 Borrow a Book
   - 4.4 Return a Book
   - 4.5 Reserve a Book
   - 4.6 View Your Loans
   - 4.7 Understanding Fines
5. [Staff Guide](#5-staff-guide)
6. [Librarian Guide](#6-librarian-guide)
   - 6.1 Manage Books
   - 6.2 Manage Members
   - 6.3 Manage Loans
   - 6.4 Manage Reservations
   - 6.5 View Outstanding Fines
   - 6.6 Sync Overdue Statuses
7. [Library Borrowing Rules](#7-library-borrowing-rules)
8. [Frequently Asked Questions (FAQ)](#8-frequently-asked-questions-faq)
9. [Glossary](#9-glossary)

---

## 1. Introduction

The **Limkokwing University Library Management System** is a digital platform that allows you to:

- Search for books in the library catalog
- Borrow and return books
- Reserve books that are currently on loan
- Track your active loans and due dates
- View outstanding fines

The system is accessed through a **web browser** using the interactive API interface at:

> **http://127.0.0.1:8000/docs**

This page (called **Swagger UI**) lets you use all library features by filling in forms and clicking buttons — no technical knowledge required.

---

## 2. Getting Started — How to Log In

### Step 1 — Open the System

Open your web browser and go to:
```
http://127.0.0.1:8000/docs
```

You will see the **Limkokwing University Library Management System** API page with a list of operations.

---

### Step 2 — Find the Login Form

Scroll down and click on the green **POST** bar next to `/auth/login`.

![Login section](login_section)

Click **"Try it out"** button (top right of the expanded section).

---

### Step 3 — Enter Your Credentials

Fill in the form:

| Field | What to enter |
|-------|--------------|
| `username` | Your **User ID** (e.g. `LU905004615`) |
| `password` | Your password (e.g. `student123`) |

Click the blue **"Execute"** button.

---

### Step 4 — Copy Your Token

Scroll down to the **Server response** section. You will see a response like this:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": "LU905004615",
  "name": "Lamarana Sow",
  "role": "Student"
}
```

**Copy the entire value** of `access_token` (the long string starting with `eyJ...`).

---

### Step 5 — Authorize Yourself

Scroll back to the **very top** of the page and click the green **"Authorize 🔒"** button.

In the popup:
1. In the **Value** field, paste your token
2. Click **"Authorize"**
3. Click **"Close"**

You are now logged in! The lock icon will turn **closed**, meaning all endpoints are unlocked for your role.

> **Your login session lasts 8 hours.** After that, you will need to log in again.

---

### Default Login Credentials

| Role | User ID | Password |
|------|---------|----------|
| Librarian | `LIB001` | `librarian123` |
| Student | `LU905004615` | `student123` |
| Student | `LU905012345` | `student123` |
| Student | `LU905098765` | `student123` |
| Staff | `LUS9876` | `staff123` |
| Staff | `LUS1234` | `staff123` |

---

## 3. Understanding Your Role

The system has **3 roles**, each with different permissions:

| What you can do | Student | Staff | Librarian |
|----------------|---------|-------|-----------|
| View book catalog | Yes | Yes | Yes |
| Search books | Yes | Yes | Yes |
| Borrow books | Yes (max 3) | Yes (max 5) | Yes (max 10) |
| Return books | Own only | Own only | Any |
| Reserve books | Yes | Yes | Yes |
| View own loans | Yes | Yes | Yes |
| View all loans | No | No | Yes |
| Add/edit/delete books | No | No | Yes |
| View all members | No | No | Yes |
| Create member accounts | No | No | Yes |
| View all fines | No | No | Yes |

---

## 4. Student Guide

### 4.1 View Your Profile

After logging in, use **GET /auth/me** to view your profile.

1. Click on **GET /auth/me** (under the **Authentication** section)
2. Click **"Try it out"** → **"Execute"**
3. Your profile will appear, including:
   - Your name, email, and role
   - Number of active loans
   - Total outstanding fine (in RM)

---

### 4.2 Search for Books

Use **GET /books/** to browse and search the catalog.

1. Click **GET /books/** (under the **Books** section)
2. Click **"Try it out"**
3. Fill in any of these optional search fields:

| Field | Example | What it does |
|-------|---------|--------------|
| `search` | `python` | Searches title, author, ISBN |
| `category` | `Computing & IT` | Filter by faculty category |
| `available_only` | `true` | Show only books you can borrow now |
| `limit` | `10` | Number of results to show |

4. Click **"Execute"** — results appear below

**Available Categories:**
- Creative Multimedia
- Computing & IT
- Design Innovation
- Architecture & Built Environment
- Business & Globalization
- Fashion & Textile
- Music & Sound Production
- Film & Television
- General Reference
- Periodicals & Journals

#### Finding a specific book by ISBN

Use **GET /books/{isbn}**:
1. Click on it → **"Try it out"**
2. Enter the ISBN (e.g. `978-0-13-468599-1`)
3. Click **"Execute"**

---

### 4.3 Borrow a Book

Use **POST /loans/borrow** to borrow a book.

**Before borrowing, check:**
- You have fewer than 3 active loans (student limit)
- Your outstanding fine is below RM 10.00
- The book has `available_copies > 0`

**Steps:**
1. Find the book's ISBN using the search (see 4.2 above)
2. Click **POST /loans/borrow** (under **Loans & Returns**)
3. Click **"Try it out"**
4. In the **Request body**, replace the example with:
   ```json
   {
     "book_isbn": "978-0-13-468599-1"
   }
   ```
5. Click **"Execute"**

**Successful response example:**
```json
{
  "id": 5,
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

**Note your `due_date`** — you must return the book by this date to avoid fines!

---

### 4.4 Return a Book

Use **POST /loans/return/{loan_id}** to return a book.

1. First, find your **Loan ID** by viewing your loans (see 4.6 below)
2. Click **POST /loans/return/{loan_id}**
3. Click **"Try it out"**
4. Enter your `loan_id` (e.g. `5`)
5. Click **"Execute"**

**Successful response (on time):**
```json
{
  "status": "Returned",
  "fine_amount": 0.0,
  "return_date": "2026-06-10"
}
```

**Successful response (overdue — 3 days late as Student):**
```json
{
  "status": "Returned",
  "fine_amount": 1.50,
  "return_date": "2026-06-24"
}
```
> **RM 0.50 × 3 days late = RM 1.50 fine**

---

### 4.5 Reserve a Book

If a book shows `available_copies: 0`, you can reserve it.

Use **POST /reservations/**:

1. Click **POST /reservations/** (under **Reservations**)
2. Click **"Try it out"**
3. In the **Request body**:
   ```json
   {
     "book_isbn": "978-0-13-468599-1"
   }
   ```
4. Click **"Execute"**

> **Note:** You cannot reserve a book that has available copies. Borrow it directly instead.

**To cancel a reservation:**
1. View your reservations to find the reservation ID (see below)
2. Click **DELETE /reservations/{reservation_id}/cancel**
3. Enter your reservation ID → **"Execute"**

---

### 4.6 View Your Loans

Use **GET /loans/** to see all your loans:

1. Click **GET /loans/**
2. Click **"Try it out"**
3. Optionally filter by status:
   - `Borrowed` — currently with you
   - `Overdue` — past due date
   - `Returned` — completed loans
4. Click **"Execute"**

Each loan shows:
- `id` — your loan ID (needed for returning)
- `book_title` — the book name
- `borrow_date` — when you borrowed it
- `due_date` — when it must be returned
- `status` — current status
- `fine_amount` — any accumulated fine

---

### 4.7 Understanding Fines

**As a Student:**
- Fine rate: **RM 0.50 per day overdue**
- If your total outstanding fines reach **RM 10.00**, your borrowing will be **blocked**

**Example:**
```
You borrowed a book due on June 21.
You return it on June 25 (4 days late).
Fine = 4 × RM 0.50 = RM 2.00
```

**To pay fines:** Visit the library counter in person. Fines cannot be paid through this system.

**Check your fines:** Look at your profile via **GET /auth/me** — the `total_outstanding_fine` field shows your current balance.

---

## 5. Staff Guide

Staff members follow the **same steps as Students** but with different limits:

| Rule | Staff Value |
|------|------------|
| Max books borrowed at once | **5 books** |
| Loan duration | **30 days** |
| Fine rate | **RM 0.20 per day** |
| Fine suspension threshold | **RM 10.00** |

All operations (borrow, return, reserve, view loans) work identically to the Student Guide above. Refer to **Section 4** for step-by-step instructions.

---

## 6. Librarian Guide

Librarians have **full access** to all features including management of books, members, loans, and reservations.

### 6.1 Manage Books

#### Add a New Book
Use **POST /books/**:

1. Click **POST /books/** → **"Try it out"**
2. Fill in the request body:
```json
{
  "isbn": "978-0-13-110163-9",
  "title": "Introduction to Algorithms",
  "author": "Thomas H. Cormen",
  "publisher": "MIT Press",
  "year_published": 2022,
  "category": "Computing & IT",
  "total_copies": 3,
  "location": "Level 2, Aisle A",
  "description": "A comprehensive introduction to algorithms."
}
```
3. Click **"Execute"**

**Rules:**
- ISBN must be unique in the system
- Category must be one of the 10 allowed Limkokwing categories
- `total_copies` must be between 1 and 100

#### Update a Book
Use **PATCH /books/{isbn}**:

1. Click **PATCH /books/{isbn}** → **"Try it out"**
2. Enter the ISBN
3. Only include the fields you want to change:
```json
{
  "total_copies": 5,
  "location": "Level 2, Aisle B"
}
```
4. Click **"Execute"**

> **Note:** If you increase `total_copies`, `available_copies` increases by the same amount automatically.

#### Delete a Book
Use **DELETE /books/{isbn}**:

> **Warning:** A book cannot be deleted if any copies are currently on loan.

1. Click **DELETE /books/{isbn}** → **"Try it out"**
2. Enter the ISBN → **"Execute"**

---

### 6.2 Manage Members

#### Create a Member Account
Use **POST /users/**:

1. Click **POST /users/** (under Users) → **"Try it out"**
2. Fill in:
```json
{
  "id": "LU905099999",
  "name": "New Student Name",
  "email": "new.student@student.limkokwing.edu.my",
  "password": "initialpassword",
  "role": "Student"
}
```
3. Click **"Execute"**

Roles: `Student`, `Staff`, or `Librarian`

#### View All Members
Use **GET /users/**:

Filter options:
- `role` — filter by `Student`, `Staff`, or `Librarian`
- `is_active` — `true` or `false`

#### Deactivate a Member (instead of deleting)
Use **PATCH /users/{user_id}**:
```json
{
  "is_active": false
}
```
Deactivated members cannot log in or borrow books.

#### Delete a Member
Use **DELETE /users/{user_id}**:

> **Warning:** Cannot delete a user who has active loans. All their books must be returned first.

---

### 6.3 Manage Loans

#### Borrow a Book on Behalf of a Member
Use **POST /loans/borrow** with the `user_id` query parameter:

1. Click **POST /loans/borrow** → **"Try it out"**
2. In the **Parameters** section, enter `user_id` = the member's ID
3. In the request body: `{"book_isbn": "978-0-13-468599-1"}`
4. Click **"Execute"**

#### Return a Book for a Member
Use **POST /loans/return/{loan_id}**:
- Librarians can return any loan (not just their own)

#### View All Loans in the System
Use **GET /loans/**:
- Leave `user_id` empty to see **all** loans
- Filter by `status`: `Borrowed`, `Overdue`, or `Returned`

#### View a Specific Member's Loans
Use **GET /loans/**, set `user_id` to the member's ID (e.g. `LU905004615`)

---

### 6.4 Manage Reservations

#### View All Pending Reservations
Use **GET /reservations/**, set `status` to `Pending`

#### Fulfil a Reservation
When a member comes to pick up their reserved book:

1. Click **POST /reservations/{reservation_id}/fulfil** → **"Try it out"**
2. Enter the `reservation_id`
3. Click **"Execute"**

> This changes the reservation status to `Fulfilled`. The actual borrowing still needs to be recorded using **POST /loans/borrow**.

#### Cancel a Reservation (on behalf of member)
Use **DELETE /reservations/{reservation_id}/cancel**

---

### 6.5 View Outstanding Fines

Use **GET /users/fines** to see all members with unpaid fines:

1. Click **GET /users/fines** → **"Try it out"** → **"Execute"**
2. Results show each member's:
   - Name and User ID
   - Total outstanding fine
   - Each overdue loan contributing to the fine

This is useful for identifying members who should be contacted to return books or pay fines.

---

### 6.6 Sync Overdue Statuses

Over time, some loans may have passed their due date but still show as `Borrowed`. Run a sync to update them:

Use **POST /loans/sync-overdue**:

1. Click → **"Try it out"** → **"Execute"**
2. The response tells you how many loans were updated to `Overdue`

> **Best practice:** Run this daily (e.g. each morning when the library opens).

---

## 7. Library Borrowing Rules

### Loan Durations and Limits

| Role | Max Books at Once | Loan Duration | Return Deadline |
|------|-------------------|---------------|-----------------|
| **Student** | 3 books | 14 days | 2 weeks from borrow date |
| **Staff** | 5 books | 30 days | 1 month from borrow date |
| **Librarian** | 10 books | 60 days | 2 months from borrow date |

### Fine Rates

| Role | Fine Per Overdue Day | Suspended At |
|------|---------------------|--------------|
| **Student** | RM 0.50 / day | RM 10.00 total |
| **Staff** | RM 0.20 / day | RM 10.00 total |
| **Librarian** | No fines | N/A |

### What Happens When You're Suspended?

If your **outstanding fines reach RM 10.00**, you will see this error when trying to borrow:

> *"Your account is blocked due to outstanding fines of RM 10.50. Please settle fines exceeding RM 10.00 at the library counter."*

You must **pay your fines at the library counter** before you can borrow again.

### Reservation Rules

- You can only reserve a book if **all copies are currently on loan**
- If a copy is available, you must borrow it directly
- You cannot have two pending reservations for the same book
- You can cancel a pending reservation at any time

---

## 8. Frequently Asked Questions (FAQ)

**Q: I get "401 Unauthorized" — what does this mean?**
> Your login token is missing or has expired. Scroll to the top of the page, click **Authorize 🔒**, and log in again.

**Q: I get "403 Forbidden" — what does this mean?**
> You are trying to do something that your role does not allow. For example, only Librarians can add books or view all members.

**Q: I tried to borrow a book but got an error about "borrow limit".**
> You have reached the maximum number of books for your role. Return a book before borrowing another one. Students: max 3. Staff: max 5.

**Q: The book I want shows `available_copies: 0`. What can I do?**
> Use **POST /reservations/** to reserve it. You will be notified when it becomes available (the librarian will fulfil your reservation).

**Q: I returned a book but it still shows as "Borrowed".**
> Contact the librarian. They can check the loan ID and process the return on your behalf using **POST /loans/return/{loan_id}**.

**Q: I can't borrow any books — it says I have outstanding fines.**
> Your total fines have reached RM 10.00. Visit the library counter to pay. Once the librarian clears your account, borrowing will be re-enabled.

**Q: How do I know when my book is due?**
> View your loans using **GET /loans/**. Each loan shows a `due_date` field.

**Q: I can't see other students' loans.**
> This is by design. Students and Staff can only see their own loans. Only Librarians can view all loans.

**Q: How do I register a new account?**
> Use **POST /auth/register**. If you are a student, your User ID should follow the format `LU` followed by your student number (e.g. `LU905004615`). You can self-register with the `Student` or `Staff` role. To create a `Librarian` account, ask the existing librarian to create it via **POST /users/**.

**Q: Can I change my password?**
> Password changes are not yet self-service. Ask the Librarian to update your account via **PATCH /users/{id}**.

---

## 9. Glossary

| Term | Definition |
|------|-----------|
| **ISBN** | International Standard Book Number — unique identifier for each book (e.g. `978-0-13-468599-1`) |
| **JWT Token** | JSON Web Token — a secure string that proves your identity after login |
| **Loan** | A record of a book being borrowed by a member |
| **Due Date** | The deadline by which a borrowed book must be returned |
| **Fine** | A monetary penalty (in RM) charged for returning a book after its due date |
| **Reservation** | A request to hold a book that is currently on loan |
| **Available Copies** | The number of physical copies of a book that can be borrowed right now |
| **Overdue** | A loan whose due date has passed and the book has not been returned |
| **Suspension** | When a member's account is blocked from borrowing due to unpaid fines ≥ RM 10.00 |
| **Swagger UI** | The interactive web interface at `/docs` used to access all system features |
| **Librarian** | Library staff with full administrative access |
| **Bearer Token** | The format of the JWT token used in API requests (`Bearer eyJ...`) |

---

*For technical support, contact the Limkokwing University IT Department.*
*Library counter: Ground Floor, Limkokwing University Main Campus.*

---

*End of User Manual*
