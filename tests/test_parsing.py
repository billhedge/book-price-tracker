from decimal import Decimal, InvalidOperation
from pathlib import Path

import pytest

import booktracker.exceptions as ex
import booktracker.parsing as p
from booktracker.data import Book

GOOD_FIXTURE = Path(__file__).parent / "fixtures/category-horror-page1.html"
BAD_FIXTURE_NO_ID = Path(__file__).parent / "fixtures/category-horror-page1-2nd-book-no-id.html"
BAD_FIXTURE_GARBLED_PRICE = (
    Path(__file__).parent / "fixtures/category-horror-page1-5th-book-garbled-price.html"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


@pytest.mark.parametrize(("text", "expected"), [("£23.37", Decimal("23.37"))], ids=["normal"])
def test_parse_price_valid(text: str, expected: Decimal) -> None:
    assert p._parse_price(text) == expected


@pytest.mark.parametrize("text", ("kjn", "£", ""), ids=["invalid", "only-pound", "empty"])
def test_parse_price_invalid(text: str) -> None:
    with pytest.raises(ex.ParseError) as exc_info:
        p._parse_price(text)
    assert type(exc_info.value) is ex.ParseError
    assert type(exc_info.value.__cause__) is InvalidOperation


@pytest.mark.parametrize(
    ("text", "expected"),
    (
        ("../../../security_925/index.html", 925),
        ("../../../night-shift-night-shift-1-20_335/index.html", 335),
    ),
    ids=["valid_925", "valid_335"],
)
def test_parse_book_id_valid(text, expected):
    assert p._parse_book_id(text) == expected


@pytest.mark.parametrize("text", ("_xxx", "xyz", ""), ids=["underscore_xxx", "xyz", "blank"])
def test_parse_book_id_invalid(text):
    with pytest.raises(ex.ParseError) as exc_info:
        p._parse_book_id(text)
    assert type(exc_info.value) is ex.ParseError
    assert exc_info.value.__cause__ is None


def test_check_book_count():
    books = p.parse_books(_read(GOOD_FIXTURE))

    assert len(books) == 17


def test_first_book():
    books = p.parse_books(_read(GOOD_FIXTURE))

    assert books[0] == Book(
        book_id=925, title="Security", price=Decimal("39.25"), availability="In stock"
    )


def test_missing_id_raises():
    with pytest.raises(ex.ParseError) as exc_info:
        p.parse_books(_read(BAD_FIXTURE_NO_ID))
    assert type(exc_info.value) is ex.ParseError
    assert exc_info.value.__cause__ is None


def test_garbled_price_raises():
    with pytest.raises(ex.ParseError) as exc_info:
        p.parse_books(_read(BAD_FIXTURE_GARBLED_PRICE))
    assert type(exc_info.value) is ex.ParseError
    assert type(exc_info.value.__cause__) is InvalidOperation


def test_full_titles():
    books = p.parse_books(_read(GOOD_FIXTURE))
    titles = {book.book_id: book.title for book in books}
    assert titles[309] == "'Salem's Lot"
    assert titles[390] == "Red Dragon (Hannibal Lecter #1)"


def test_no_books_raises():
    with pytest.raises(ex.ParseError) as exc_info:
        p.parse_books("<html></html>")
    assert type(exc_info.value) is ex.ParseError
