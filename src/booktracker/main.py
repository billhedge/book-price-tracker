import argparse

import requests

from booktracker.data import Book

DEFAULT_URL = "https://books.toscrape.com/catalogue/category/books/horror_31/index.html"


def format_book(book: Book) -> str:  # one line: id, price, availability, title
    return ""  # placeholder


def main(argv: list[str] | None = None, session: requests.Session | None = None) -> int:
    # TODO: argparse, one optional positional url (default DEFAULT_URL)
    # TODO: session = session or requests.Session()
    # TODO: fetch, parse, print each line; AppError -> stderr, return 1
    parser = argparse.ArgumentParser(
        prog="booktracker",
        description="Print the books on a books.toscrape.com listing page.",
    )
    parser.add_argument("url", nargs="?", default=DEFAULT_URL, help="listing page URL")
    parser.parse_args(argv)
    return 0
