import sqlite3
from dataclasses import dataclass
from decimal import Decimal

from booktracker.data import Book
from booktracker.storage import latest_timestamps, load_scrape


@dataclass(frozen=True)
class PriceChange:
    book_id: int
    title: str
    old_price: Decimal
    new_price: Decimal


def price_changes(old: dict[int, Book], new: dict[int, Book]) -> list[PriceChange]:
    changes: list[PriceChange] = [
        PriceChange(
            book_id=book_id,
            title=new[book_id].title,
            old_price=old[book_id].price,
            new_price=new[book_id].price,
        )
        for book_id in sorted(old.keys() & new.keys())
        if old[book_id].price != new[book_id].price
    ]

    return changes


def format_changes(changes: list[PriceChange]) -> list[str]:
    return [
        f"{change.book_id} {change.old_price:.2f} -> {change.new_price:.2f} {change.title}"
        for change in changes
    ]


def check_changes(conn: sqlite3.Connection, url: str) -> list[str]:
    stamps = latest_timestamps(conn, url)
    if len(stamps) < 2:
        return [f"Need more than one scrape for {url} to compare."]
    new = load_scrape(conn, url, stamps[0])
    old = load_scrape(conn, url, stamps[1])
    changes = price_changes(old, new)
    if len(changes) == 0:
        return [f"No price changes for {url}."]
    return format_changes(changes)
