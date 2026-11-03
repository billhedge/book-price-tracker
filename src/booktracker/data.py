from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Book:
    book_id: int
    title: str
    price: Decimal
    availability: str
