import sqlite3
from collections.abc import Iterable
from pathlib import Path

from booktracker.data import Book
from booktracker.exceptions import StorageError

_SCHEMA = """
CREATE TABLE IF NOT EXISTS prices (
    scraped_at   TEXT    NOT NULL,
    url          TEXT    NOT NULL,
    book_id      INTEGER NOT NULL,
    title        TEXT    NOT NULL,
    price        TEXT    NOT NULL,
    availability TEXT    NOT NULL
)
"""


def connect(path: str | Path) -> sqlite3.Connection:
    try:
        db = sqlite3.connect(path)
        db.execute(_SCHEMA)
    except sqlite3.Error as e:
        raise StorageError(f"Unable to open database file {path}: {e}") from e
    return db


def save_scrape(conn: sqlite3.Connection, url: str, scraped_at: str, books: Iterable[Book]) -> None:
    rows: list[tuple[str, str, int, str, str, str]] = []
    rows.extend(
        (scraped_at, url, book.book_id, book.title, str(book.price), book.availability)
        for book in books
    )
    try:
        with conn:
            conn.executemany("INSERT INTO prices VALUES (?, ?, ?, ?, ?, ?)", rows)
    except sqlite3.Error as e:
        raise StorageError(f"Unable to save scrape to db: {e}") from e
