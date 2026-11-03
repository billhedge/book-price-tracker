import decimal
import re
from decimal import Decimal

from bs4 import BeautifulSoup, Tag

import booktracker.exceptions as ex
from booktracker.data import Book

_BOOK_ID = re.compile(r"_(\d+)(?=/|$)")  # digits after the last "_", before "/index.html"


def parse_books(html: str) -> list[Book]:
    soup = BeautifulSoup(html, "html.parser")
    pods = soup.select("article.product_pod")
    if len(pods) == 0:
        raise ex.ParseError("No books were found in this page.")
    return [_parse_pod(pod) for pod in pods]


def _parse_pod(pod: Tag) -> Book:
    link = _required(pod, "h3 a")
    book_id = _parse_book_id(_attr(link, "href"))  # href is required, but may not contain an ID
    title = _attr(link, "title")
    price = _parse_price(_required(pod, "p.price_color").get_text(strip=True))
    availability = _required(pod, "p.availability").get_text(strip=True)
    book = Book(book_id, title, price, availability)
    return book


def _parse_price(text: str) -> Decimal:  # "£23.37" -> Decimal("23.37")
    try:
        return Decimal(text.strip("£"))
    except decimal.InvalidOperation as e:
        raise ex.ParseError(f'Unable to return decimal from "{text}".') from e


def _parse_book_id(href: str) -> int:  # no match -> ParseError
    match = _BOOK_ID.search(href)
    if match is None:
        raise (ex.ParseError(f"Unable to find an ID in URL {href}."))
    else:
        return int(match.group(1))


def _required(parent: Tag, selector: str) -> Tag:
    found = parent.select_one(selector)
    if found is None:
        raise ex.ParseError(f"No element matches {selector!r}")
    return found


def _attr(tag: Tag, name: str) -> str:
    value = tag.get(name)
    if not isinstance(value, str):
        raise ex.ParseError(f"<{tag.name}> has no single {name!r} attribute")
    return value
