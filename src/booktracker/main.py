import argparse
import io
import sys
from contextlib import closing
from datetime import datetime, timezone

import requests

import booktracker.exceptions as ex
from booktracker.changes import check_changes
from booktracker.data import Book
from booktracker.network import fetch_page
from booktracker.parsing import parse_books
from booktracker.storage import connect, save_scrape

DEFAULT_URL = "https://books.toscrape.com/catalogue/category/books/horror_31/index.html"

GAP = "  "


def format_book(book: Book, widths: tuple[int, int, int, int]) -> str:
    id_w, price_w, avail_w, _ = widths

    return GAP.join(
        (
            f"{book.book_id:>{id_w}}",
            f"{book.price:>{price_w}.2f}",
            f"{book.availability:<{avail_w}}",
            f"{book.title}",
        )
    )


def get_widths(books: list[Book], labels: tuple[str, ...]) -> tuple[int, int, int, int]:
    l_book_id, l_price, l_availability, l_title = labels
    return (
        max([len(l_book_id), *(len(str(b.book_id)) for b in books)]),
        max([len(l_price), *(len(f"{b.price:.2f}") for b in books)]),
        max([len(l_availability), *(len(b.availability) for b in books)]),
        max([len(l_title), *(len(b.title) for b in books)]),
    )


def build_table(books: list[Book]) -> str:
    labels = ("Book ID", "Price (£)", "Availability", "Title")
    col_widths = get_widths(books, labels)
    columns = tuple((label, width) for label, width in zip(labels, col_widths, strict=True))

    header = GAP.join(
        f"{label:>{width}}"
        if label in ("Book ID", "Price (£)")
        else (f"{label}" if label == "Title" else f"{label:<{width}}")
        for label, width in columns
    )

    rule = GAP.join(["-" * w for _, w in columns])

    book_rows = [format_book(book, col_widths) for book in books]
    return "\n".join([header, rule, *book_rows])


def main(argv: list[str] | None = None, session: requests.Session | None = None) -> int:
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        prog="booktracker",
        description="Print the books on a books.toscrape.com listing page.",
    )
    parser.add_argument("url", nargs="?", default=DEFAULT_URL, help="listing page URL")
    parser.add_argument("--db", default="booktracker.sqlite", help="local cache file name")
    parser.add_argument("--changes", action="store_true", help="check for price changes")
    args = parser.parse_args(argv)
    session = session or requests.Session()
    try:
        if args.changes:
            with closing(connect(args.db)) as conn:
                formatted_changes = check_changes(conn, url=args.url)
            for change in formatted_changes:
                print(change)
            return 0
        books = parse_books(fetch_page(session, args.url))
        # saving the table before printing
        scraped_at = datetime.now(timezone.utc).isoformat()
        with closing(connect(args.db)) as conn:
            save_scrape(conn, args.url, scraped_at, books)

    except ex.AppError as e:
        print(f"booktracker: {e}", file=sys.stderr)
        return 1
    out_string = build_table(books)
    print(out_string)

    return 0
