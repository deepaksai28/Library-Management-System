"""SQLite database setup and connection helpers."""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "library.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_database():
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                isbn TEXT UNIQUE,
                total_copies INTEGER NOT NULL CHECK(total_copies >= 1),
                available_copies INTEGER NOT NULL CHECK(
                    available_copies >= 0 AND available_copies <= total_copies
                )
            );
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                phone TEXT,
                joined_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER NOT NULL,
                member_id INTEGER NOT NULL,
                issue_date TEXT NOT NULL,
                due_date TEXT NOT NULL,
                return_date TEXT,
                status TEXT NOT NULL DEFAULT 'ISSUED'
                    CHECK(status IN ('ISSUED', 'RETURNED')),
                FOREIGN KEY(book_id) REFERENCES books(id),
                FOREIGN KEY(member_id) REFERENCES members(id)
            );
            CREATE INDEX IF NOT EXISTS idx_transactions_status
                ON transactions(status);
            CREATE INDEX IF NOT EXISTS idx_transactions_member
                ON transactions(member_id);
        """)
