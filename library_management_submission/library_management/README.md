# Library Management System — ERPNext Assignment Submission

## Overview

A custom Frappe/ERPNext app implementing a Library Management System with:
- **Library Member** DocType — member registration & membership tracking
- **Book** DocType — book catalog with copy tracking
- **Book Transaction** DocType — issue/return workflow with validation

---

## Setup Instructions

### Prerequisites
- ERPNext v14 or v15 installed (Docker or bare-metal)
- Python 3.10+
- Node.js 18+

### Installation (Bare-metal)

```bash
# 1. Navigate to your bench directory
cd frappe-bench

# 2. Create the app (if starting fresh)
bench new-app library_management

# OR clone this repository into apps/
git clone <your-repo-url> apps/library_management

# 3. Install the app on your site
bench --site library.localhost install-app library_management

# 4. Migrate the database (creates the DocType tables)
bench --site library.localhost migrate

# 5. Clear cache and restart
bench --site library.localhost clear-cache
bench restart
```

### Installation (Docker)

```bash
docker-compose -f pwd.yml exec backend bench new-app library_management
docker-compose -f pwd.yml exec backend bench --site library.localhost install-app library_management
docker-compose -f pwd.yml exec backend bench --site library.localhost migrate
```

---

## DocType Descriptions

### 1. Library Member

Stores information about library members.

**Fields:**
| Field | Type | Required | Notes |
|---|---|---|---|
| First Name | Data | Yes | |
| Last Name | Data | Yes | |
| Full Name | Data | No | Auto-computed (read-only) |
| Email Address | Data (Email) | Yes | Unique |
| Phone | Data (Phone) | No | |
| Membership Status | Select | Yes | Active / Expired / Suspended |
| Membership Date | Date | Yes | Defaults to today |
| Membership Expiry | Date | No | |
| Address | Small Text | No | |

**Auto-naming:** `LM-YYYY-#####` (e.g. LM-2024-00001)

**Validation Logic:**
- `full_name` is auto-populated from first + last name
- Expiry date cannot be before membership date
- Membership auto-set to "Expired" if expiry date has passed

---

### 2. Book

Stores the book catalog.

**Fields:**
| Field | Type | Required | Notes |
|---|---|---|---|
| Book Title | Data | Yes | |
| Author | Data | Yes | |
| ISBN | Data | No | Unique, must be 10 or 13 digits |
| Status | Select | Yes | Available / Issued / Lost / Damaged |
| Publisher | Data | No | |
| Publish Date | Date | No | |
| Genre | Select | No | Fiction, Non-Fiction, etc. |
| Description | Text Editor | No | |
| Total Copies | Int | Yes | Default: 1 |
| Available Copies | Int | No | Read-only, auto-managed |

**Auto-naming:** `BK-YYYY-#####` (e.g. BK-2024-00001)

**Validation Logic:**
- Total copies must be ≥ 1
- Available copies auto-set to total copies on new book
- ISBN validated to be 10 or 13 digits
- Status auto-updated based on available copies

---

### 3. Book Transaction

Handles issue and return of books.

**Fields:**
| Field | Type | Required | Notes |
|---|---|---|---|
| Library Member | Link → Library Member | Yes | |
| Member Name | Data | No | Fetched from member (read-only) |
| Book | Link → Book | Yes | |
| Book Title | Data | No | Fetched from book (read-only) |
| Transaction Type | Select | Yes | Issue / Return |
| Transaction Date | Date | Yes | Defaults to today |
| Due Date | Date | No | Auto-set to 14 days after issue |
| Return Date | Date | No | Auto-set on return |
| Status | Select | Yes | Open / Completed / Overdue |
| Remarks | Small Text | No | |

**Auto-naming:** `BT-YYYY-#####` (e.g. BT-2024-00001)

**Validation Logic (Issue):**
- Member must have "Active" membership
- Book must not be Lost/Damaged
- Book must have available copies ≥ 1
- Member cannot have the same book issued twice
- Due date auto-set to 14 days from transaction date
- `book.available_copies` decremented by 1 on save

**Validation Logic (Return):**
- A matching open Issue transaction must exist for the member + book
- Return date auto-set to today
- Related Issue transaction status updated to "Completed"
- `book.available_copies` incremented by 1 on save

---

## Testing Scenarios

### Test 1: Create a Library Member
1. Go to Library Member → New
2. Enter: First Name="John", Last Name="Doe", Email="john@example.com", Status="Active"
3. Save — Full Name auto-populates as "John Doe" ✅

### Test 2: Create a Book
1. Go to Book → New
2. Enter: Title="Python Programming", Author="Guido van Rossum", Total Copies=3
3. Save — Available Copies = 3, Status = Available ✅

### Test 3: Issue a Book
1. Go to Book Transaction → New
2. Select member John Doe, book "Python Programming", Type="Issue"
3. Save — Due Date auto-set, book's Available Copies becomes 2 ✅

### Test 4: Validation — Issue unavailable book
1. Set book's Total Copies to 1, issue it once
2. Try to issue again → Error: "No copies available" ✅

### Test 5: Return a Book
1. Create a Return transaction for John Doe + Python Programming
2. Save — Available Copies goes back to 3, Issue transaction marked Completed ✅

### Test 6: Expired membership
1. Set a member's expiry date to yesterday
2. Try to issue a book → Error: "Membership is Expired" ✅

---

## Git Workflow

```bash
git init
git add .
git commit -m "feat: add Library Management System with 3 DocTypes

- Add Library Member DocType with membership validation
- Add Book DocType with copy tracking and ISBN validation  
- Add Book Transaction DocType with issue/return workflow
- Implement business logic: active member check, availability check,
  auto due dates, available copy tracking"
```

---

## Time Spent

| Task | Time |
|---|---|
| Environment Setup | 2 hours |
| Library Member DocType | 1.5 hours |
| Book DocType | 1.5 hours |
| Book Transaction DocType | 2.5 hours |
| Testing & Documentation | 1.5 hours |
| **Total** | **9 hours** |
