import sqlite3
from datetime import datetime
from decimal import Decimal

import pytest

import booktracker.exceptions as ex
from booktracker.data import Book
from booktracker.storage import connect, save_scrape


def test_save_and_read_back():
    url = "https://example.com"
    id = 666
    title = "Devilry"
    price = Decimal("6.60")
    availability = "Never!"

    cnn = connect(":memory:")
    save_scrape(
        cnn, url, datetime.isoformat(datetime.now()), [Book(id, title, price, availability)]
    )

    row = cnn.execute("SELECT url, book_id, title, price, availability FROM prices").fetchone()
    assert row[0] == url
    assert row[1] == id
    assert row[2] == title
    assert row[3] == str(price)
    assert row[4] == availability


def test_two_saves_two_timestamps():
    url = "https://example.com"
    id = 666
    title = "Devilry"
    price = Decimal("6.66")
    availability = "Never!"

    cnn = connect(":memory:")
    first = "2026-11-09T00:00:00+00:00"
    second = "2026-11-09T01:00:00+00:00"
    save_scrape(cnn, url, first, [Book(id, title, price, availability)])
    save_scrape(cnn, url, second, [Book(id, title, price, availability)])
    rows = cnn.execute("SELECT DISTINCT scraped_at FROM prices").fetchall()
    assert {row[0] for row in rows} == {first, second}


def test_bad_path_raises_storage_error(tmp_path):
    with pytest.raises(ex.StorageError) as exc_info:
        _ = connect(tmp_path / "missing" / "x.sqlite")

    assert type(exc_info.value) is ex.StorageError
    assert type(exc_info.value.__cause__) is sqlite3.OperationalError
