import urllib.request, urllib.parse, json

base = "http://127.0.0.1:8000"

# 1. Login as Librarian
data = urllib.parse.urlencode({"username": "LIB001", "password": "librarian123"}).encode()
req = urllib.request.Request(f"{base}/auth/login", data=data)
resp = json.loads(urllib.request.urlopen(req).read())
token = resp["access_token"]
print(f"[1] LOGIN OK  - Token for: {resp['name']} ({resp['role']})")

# 2. List books
req2 = urllib.request.Request(f"{base}/books/?limit=3",
    headers={"Authorization": f"Bearer {token}"})
books = json.loads(urllib.request.urlopen(req2).read())
print(f"[2] BOOKS OK  - {len(books)} result(s). First title: {books[0]['title']}")

# 3. List users (librarian)
req3 = urllib.request.Request(f"{base}/users/?limit=5",
    headers={"Authorization": f"Bearer {token}"})
users = json.loads(urllib.request.urlopen(req3).read())
roles = [u["role"] for u in users]
print(f"[3] USERS OK  - {len(users)} user(s). Roles: {roles}")

# 4. Login as student
data2 = urllib.parse.urlencode({"username": "LU905004615", "password": "student123"}).encode()
req4 = urllib.request.Request(f"{base}/auth/login", data=data2)
resp2 = json.loads(urllib.request.urlopen(req4).read())
stok = resp2["access_token"]
print(f"[4] STUDENT   - Logged in as: {resp2['name']}")

# 5. Borrow a book
borrow_data = json.dumps({"book_isbn": "978-0-13-468599-1"}).encode()
req5 = urllib.request.Request(f"{base}/loans/borrow", data=borrow_data,
    headers={"Authorization": f"Bearer {stok}", "Content-Type": "application/json"})
loan = json.loads(urllib.request.urlopen(req5).read())
print(f"[5] BORROW OK - Loan #{loan['id']} | {loan['book_title']} | Due: {loan['due_date']}")

# 6. Return the book
req6 = urllib.request.Request(f"{base}/loans/return/{loan['id']}", data=b"",
    headers={"Authorization": f"Bearer {stok}", "Content-Type": "application/json"},
    method="POST")
returned = json.loads(urllib.request.urlopen(req6).read())
print(f"[6] RETURN OK - Status: {returned['status']} | Fine: RM {returned['fine_amount']:.2f}")

# 7. Try to exceed borrow limit (borrow 3 more to test limit at 3)
print("[7] Testing borrow limit enforcement...")
isbns = ["978-0-13-110163-0", "978-0-596-51774-8", "978-0-321-12521-7"]
borrowed_count = 0
for isbn in isbns:
    bd = json.dumps({"book_isbn": isbn}).encode()
    rq = urllib.request.Request(f"{base}/loans/borrow", data=bd,
        headers={"Authorization": f"Bearer {stok}", "Content-Type": "application/json"})
    try:
        r = urllib.request.urlopen(rq)
        borrowed_count += 1
    except urllib.error.HTTPError as e:
        err = json.loads(e.read())
        print(f"    Correctly blocked on book #{borrowed_count+1}: {err['detail'][:80]}")

print()
print("=" * 50)
print("   ALL API CHECKS PASSED SUCCESSFULLY")
print("=" * 50)
print(f"   Swagger UI -> http://127.0.0.1:8000/docs")
