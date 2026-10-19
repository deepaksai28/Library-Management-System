"""Command-line Library Management System using Python and SQLite."""
from datetime import date, timedelta
from database import initialize_database, get_connection


def add_book():
    title = input("Book title: ").strip()
    author = input("Author: ").strip()
    isbn = input("ISBN (optional): ").strip() or None
    try:
        copies = int(input("Number of copies: "))
        if not title or not author or copies < 1:
            raise ValueError
    except ValueError:
        print("Enter a title, author, and a positive number of copies.")
        return
    try:
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO books(title, author, isbn, total_copies, available_copies) VALUES (?, ?, ?, ?, ?)",
                (title, author, isbn, copies, copies),
            )
        print("Book added successfully.")
    except Exception as exc:
        print(f"Could not add book: {exc}")


def list_books():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, title, author, isbn, total_copies, available_copies FROM books ORDER BY title"
        ).fetchall()
    if not rows:
        print("No books found.")
        return
    print(f"\n{'ID':<4} {'TITLE':<30} {'AUTHOR':<22} {'STOCK':<12} ISBN")
    print("-" * 85)
    for row in rows:
        print(f"{row['id']:<4} {row['title'][:29]:<30} {row['author'][:21]:<22} "
              f"{row['available_copies']}/{row['total_copies']:<10} {row['isbn'] or '-'}")


def search_books():
    term = input("Search title or author: ").strip()
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT id, title, author, available_copies, total_copies
               FROM books WHERE title LIKE ? OR author LIKE ? ORDER BY title""",
            (f"%{term}%", f"%{term}%"),
        ).fetchall()
    if not rows:
        print("No matching books.")
        return
    for row in rows:
        print(f"#{row['id']} | {row['title']} — {row['author']} "
              f"| available {row['available_copies']}/{row['total_copies']}")


def update_book():
    book_id = input("Book ID to update: ").strip()
    with get_connection() as conn:
        book = conn.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
        if not book:
            print("Book not found.")
            return
        title = input(f"Title [{book['title']}]: ").strip() or book["title"]
        author = input(f"Author [{book['author']}]: ").strip() or book["author"]
        isbn = input(f"ISBN [{book['isbn'] or ''}]: ").strip() or book["isbn"]
        try:
            conn.execute("UPDATE books SET title=?, author=?, isbn=? WHERE id=?",
                         (title, author, isbn, book_id))
        except Exception as exc:
            print(f"Could not update book: {exc}")
            return
    print("Book updated.")


def delete_book():
    book_id = input("Book ID to delete: ").strip()
    with get_connection() as conn:
        book = conn.execute("SELECT id FROM books WHERE id=?", (book_id,)).fetchone()
        if not book:
            print("Book not found.")
            return
        active = conn.execute(
            "SELECT COUNT(*) AS n FROM transactions WHERE book_id=? AND status='ISSUED'",
            (book_id,),
        ).fetchone()["n"]
        if active:
            print("Cannot delete: this book has active issues.")
            return
        conn.execute("DELETE FROM books WHERE id=?", (book_id,))
    print("Book deleted.")


def add_member():
    name = input("Member name: ").strip()
    email = input("Email (optional): ").strip() or None
    phone = input("Phone (optional): ").strip() or None
    if not name:
        print("Member name is required.")
        return
    try:
        with get_connection() as conn:
            conn.execute("INSERT INTO members(name, email, phone) VALUES (?, ?, ?)",
                         (name, email, phone))
        print("Member registered.")
    except Exception as exc:
        print(f"Could not register member: {exc}")


def list_members():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, name, email, phone FROM members ORDER BY name"
        ).fetchall()
    if not rows:
        print("No members found.")
        return
    for row in rows:
        print(f"#{row['id']} | {row['name']} | {row['email'] or '-'} | {row['phone'] or '-'}")


def delete_member():
    member_id = input("Member ID to delete: ").strip()
    with get_connection() as conn:
        member = conn.execute("SELECT id FROM members WHERE id=?", (member_id,)).fetchone()
        if not member:
            print("Member not found.")
            return
        active = conn.execute(
            "SELECT COUNT(*) AS n FROM transactions WHERE member_id=? AND status='ISSUED'",
            (member_id,),
        ).fetchone()["n"]
        if active:
            print("Cannot delete: member has books not yet returned.")
            return
        conn.execute("DELETE FROM members WHERE id=?", (member_id,))
    print("Member deleted.")


def issue_book():
    book_id = input("Book ID: ").strip()
    member_id = input("Member ID: ").strip()
    raw_days = input("Loan period in days [14]: ").strip()
    try:
        loan_days = int(raw_days) if raw_days else 14
        if loan_days < 1:
            raise ValueError
    except ValueError:
        print("Loan period must be a positive integer.")
        return
    due = date.today() + timedelta(days=loan_days)
    with get_connection() as conn:
        book = conn.execute("SELECT * FROM books WHERE id=?", (book_id,)).fetchone()
        member = conn.execute("SELECT * FROM members WHERE id=?", (member_id,)).fetchone()
        if not book:
            print("Book not found.")
            return
        if not member:
            print("Member not found.")
            return
        if book["available_copies"] < 1:
            print("No copies currently available.")
            return
        conn.execute(
            """INSERT INTO transactions(book_id, member_id, issue_date, due_date, status)
               VALUES (?, ?, ?, ?, 'ISSUED')""",
            (book_id, member_id, date.today().isoformat(), due.isoformat()),
        )
        conn.execute("UPDATE books SET available_copies=available_copies-1 WHERE id=?",
                     (book_id,))
    print(f"Book issued. Due date: {due.isoformat()}")


def return_book():
    transaction_id = input("Active transaction ID: ").strip()
    with get_connection() as conn:
        transaction = conn.execute(
            "SELECT * FROM transactions WHERE id=? AND status='ISSUED'",
            (transaction_id,),
        ).fetchone()
        if not transaction:
            print("Active issue transaction not found.")
            return
        today = date.today().isoformat()
        conn.execute(
            "UPDATE transactions SET status='RETURNED', return_date=? WHERE id=?",
            (today, transaction_id),
        )
        conn.execute("UPDATE books SET available_copies=available_copies+1 WHERE id=?",
                     (transaction["book_id"],))
    print("Book returned and inventory updated.")


def list_transactions():
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT t.id, b.title, m.name AS member_name, t.issue_date, t.due_date,
                      t.return_date, t.status
               FROM transactions t
               JOIN books b ON b.id=t.book_id
               JOIN members m ON m.id=t.member_id
               ORDER BY t.id DESC"""
        ).fetchall()
    if not rows:
        print("No transactions found.")
        return
    print(f"\n{'TXN':<5} {'BOOK':<27} {'MEMBER':<20} {'ISSUED':<12} {'DUE':<12} {'STATUS':<10} RETURNED")
    print("-" * 105)
    today = date.today().isoformat()
    for row in rows:
        overdue = row["status"] == "ISSUED" and row["due_date"] < today
        status = "OVERDUE" if overdue else row["status"]
        print(f"{row['id']:<5} {row['title'][:26]:<27} {row['member_name'][:19]:<20} "
              f"{row['issue_date']:<12} {row['due_date']:<12} {status:<10} {row['return_date'] or '-'}")


def main():
    initialize_database()
    actions = {
        "1": ("Add book", add_book),
        "2": ("List books", list_books),
        "3": ("Search books", search_books),
        "4": ("Update book", update_book),
        "5": ("Delete book", delete_book),
        "6": ("Register member", add_member),
        "7": ("List members", list_members),
        "8": ("Delete member", delete_member),
        "9": ("Issue book", issue_book),
        "10": ("Return book", return_book),
        "11": ("View issue/return history (SQL JOIN)", list_transactions),
    }
    while True:
        print("\n" + "=" * 48)
        print("       LIBRARY MANAGEMENT SYSTEM")
        print("=" * 48)
        for key, (label, _) in actions.items():
            print(f"{key:>2}. {label}")
        print(" 0. Exit")
        choice = input("Choose an option: ").strip()
        if choice == "0":
            print("Goodbye!")
            break
        action = actions.get(choice)
        if not action:
            print("Invalid option. Try again.")
            continue
        try:
            action[1]()
        except (ValueError, TypeError) as exc:
            print(f"Invalid input: {exc}")
        except Exception as exc:
            print(f"Operation failed: {exc}")


if __name__ == "__main__":
    main()
