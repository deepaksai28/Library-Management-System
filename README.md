# Library Management System

A command-line library management application built with **Python 3** and **SQLite**. It manages books, members, and issue/return transactions using relational tables and SQL queries.

## Features

- **Book CRUD:** add, list, search, update, and delete books.
- **Member management:** register, list, and delete members.
- **Issue books:** validates book/member IDs, checks stock, records issue and due dates, and reduces available inventory.
- **Return books:** records the return date and restores available inventory.
- **Due-date tracking:** flags active transactions as `OVERDUE` when the due date has passed.
- **Relational SQL JOINs:** transaction history displays the associated book and member.
- **Data integrity:** foreign keys, uniqueness constraints, checks, and indexes.
- **Local storage:** the SQLite database is generated automatically and is excluded from Git.

## Requirements

- Python 3.9 or newer
- No third-party packages required; SQLite is included with Python.

## Run the project

```bash
git clone https://github.com/deepaksai28/Library-Management-System.git
cd Library-Management-System
python main.py
```

On Windows, if `python` is not recognized, try `py main.py`.

The first run creates `library.db` in the project directory. Add books and members before issuing a book.

## Database schema

- `books`: title, author, ISBN, total copies, and available copies.
- `members`: member name, email, phone, and join timestamp.
- `transactions`: book/member foreign keys, issue date, due date, return date, and status.

The transaction history uses `JOIN` across `transactions`, `books`, and `members`.

## Example workflow

1. Select **1** to add a book.
2. Select **6** to register a member.
3. Select **9** to issue a book using its book ID and member ID.
4. Select **11** to view transaction history and due status.
5. Select **10** to return the book using the active transaction ID.

## Project structure

```text
Library-Management-System/
├── main.py          # CLI menu and library operations
├── database.py      # SQLite schema and connection helper
├── README.md        # Setup and usage instructions
├── .gitignore       # Excludes local database and Python cache
└── requirements.txt # No external dependencies
```

## Note on the database

This implementation uses **SQLite**, not MySQL. SQLite is file-based and does not require a separate database server.
