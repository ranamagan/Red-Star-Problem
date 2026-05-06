# Self-Review — Library Management System

## Submission Checklist

- [x] Environment set up and ERPNext running
- [x] Library Member DocType created with all required fields
- [x] Book DocType created with all required fields
- [x] Book Transaction DocType created with all required fields
- [x] Validation logic implemented in Python controllers
- [x] Git repository initialized with meaningful commit messages
- [x] README with setup instructions written
- [x] Testing documented

---

## What I Built

### Library Member
- Stores member personal info and membership status
- Auto-populates `full_name` from first + last name
- Validates that expiry date is after membership date
- Auto-sets status to "Expired" if expiry date has passed

### Book
- Stores book catalog with ISBN, author, publisher, genre
- Tracks total and available copies
- Validates ISBN format (10 or 13 digits)
- Auto-manages `available_copies` and `status`

### Book Transaction
- Links Member ↔ Book with Issue/Return workflow
- On Issue: validates active membership, availability, no duplicate issues
- On Return: validates open issue exists, closes it, updates book copies
- Auto-sets due date to 14 days; return date to today on return

---

## Challenges Faced

1. **on_submit vs validate**: Decided to use `on_submit` for updating Book's `available_copies` so the count only changes when the transaction is fully committed.

2. **Return validation**: Making sure a Return only works if there is an open Issue for that exact member-book pair required a `frappe.db.exists()` query with multiple filters.

3. **Auto-expiry**: Implemented membership auto-expiry in `validate()` so it triggers every time the member record is saved or viewed.

---

## What I Would Improve With More Time

- Add a **Frappe Web Form** so members can self-register online
- Add an **overdue reminder** scheduled job that emails members when due date has passed
- Add a **report** showing all currently issued books and their due dates
- Add a **dashboard** with charts (books by genre, transactions per month)
- Write automated tests using `frappe.tests.utils`

---

## Code Quality Notes

- All validation logic is in `validate()` — never in `on_submit()` alone
- Business side-effects (updating book copies) are in `on_submit()`
- Error messages are user-friendly and actionable
- Field labels are clear and consistent
- PEP 8 style followed in Python files
