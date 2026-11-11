from decimal import Decimal
from pathlib import Path

from booktracker.data import Book

GOOD_FIXTURE = Path(__file__).parent / "fixtures/category-horror-page1.html"
BAD_FIXTURE_NO_ID = Path(__file__).parent / "fixtures/category-horror-page1-2nd-book-no-id.html"

BOOKS1 = [
    Book(123, "Title 1", Decimal("12.50"), "In Stock"),
    Book(111, "Title 2", Decimal("14.95"), "In Stock"),
    Book(430, "Title 3", Decimal("59.21"), "In Stock"),
]
BOOKS_UP = [
    Book(123, "Title 1", Decimal("12.50"), "In Stock"),
    Book(111, "Title 2", Decimal("14.95"), "In Stock"),
    Book(430, "Title 3", Decimal("75.00"), "In Stock"),
]
BOOKS_DOWN = [
    Book(123, "Title 1", Decimal("12.50"), "In Stock"),
    Book(111, "Title 2", Decimal("5.99"), "In Stock"),
    Book(430, "Title 3", Decimal("59.21"), "In Stock"),
]
BOOKS_DECIMAL = [
    Book(123, "Title 1", Decimal("12.5"), "In Stock"),
    Book(111, "Title 2", Decimal("14.95"), "In Stock"),
    Book(430, "Title 3", Decimal("59.21"), "In Stock"),
]

BOOKS_PLUS_ONE = [
    Book(123, "Title 1", Decimal("12.50"), "In Stock"),
    Book(111, "Title 2", Decimal("14.95"), "In Stock"),
    Book(430, "Title 3", Decimal("59.21"), "In Stock"),
    Book(999, "Title 4", Decimal("99.99"), "In Stock"),
]

BOOKS_MULTIPLE_CHANGES = [
    Book(430, "Title 3", Decimal("75.00"), "In Stock"),
    Book(123, "Title 1", Decimal("12.50"), "In Stock"),
    Book(111, "Title 2", Decimal("5.99"), "In Stock"),
]

BOOKS_THIRD_SCRAPE = [
    Book(123, "Title 1", Decimal("12.50"), "In Stock"),
    Book(111, "Title 2", Decimal("14.95"), "In Stock"),
    Book(430, "Title 3", Decimal("59.21"), "In Stock"),
    Book(999, "Title 4", Decimal("99.90"), "In Stock"),
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class FakeResponse:
    def __init__(self, content: bytes, status_code: int = 200) -> None:
        self.content = content
        self.status_code = status_code


class FakeSession:
    """
    session will need # type: ignore[arg-type] where it's passed in place of requests.Session
    """

    def __init__(self, content: bytes = b"", status_code: int = 200) -> None:
        self.content = content
        self.status_code = status_code
        self.calls: list[tuple[str, float | None]] = []

    def get(self, url: str, timeout: float | None = None) -> FakeResponse:
        self.calls.append((url, timeout))
        return FakeResponse(self.content, self.status_code)


class RaisingSession:
    """a session whose get() raises whatever exception you give it"""

    def __init__(self, exc):
        self.exc = exc

    def get(self, url, params=None, timeout=None):
        raise self.exc
