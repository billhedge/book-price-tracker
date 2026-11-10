from contextlib import closing
from decimal import Decimal

import pytest
import requests

from booktracker.data import Book
from booktracker.main import DEFAULT_URL, build_table, main
from booktracker.storage import connect
from fakes import BAD_FIXTURE_NO_ID, GOOD_FIXTURE, FakeSession, RaisingSession


def test_success_prints_table(capsys, tmp_path) -> None:
    session = FakeSession(GOOD_FIXTURE.read_bytes())
    db_path = tmp_path / "x.sqlite"
    code = main(["--db", str(db_path)], session=session)  # type: ignore[arg-type]

    out, err = capsys.readouterr()
    lines = out.splitlines()

    assert code == 0
    assert len(lines) == 19  # header + rule + books
    assert err == ""
    assert session.calls == [(DEFAULT_URL, 10)]
    assert lines[2] == "    925      39.25  In stock      Security"
    assert any("Security" in row for row in lines)

    with closing(connect(db_path)) as cnn:
        rows = cnn.execute(
            "SELECT COUNT(*), COUNT(DISTINCT scraped_at), COUNT(DISTINCT url), url FROM prices"
        )
        rowcount, distinct_timestamps, distinct_url, scraped_url = rows.fetchone()
    assert rowcount == 17
    assert distinct_timestamps == 1
    assert distinct_url == 1
    assert scraped_url == DEFAULT_URL


def test_custom_url_is_fetched(capsys, tmp_path) -> None:
    session = FakeSession(GOOD_FIXTURE.read_bytes())
    url = "https://example.com/books"
    code = main([url, "--db", str(tmp_path / "x.sqlite")], session=session)  # type: ignore[arg-type]
    out, err = capsys.readouterr()

    assert code == 0
    assert out
    assert err == ""
    assert session.calls == [(url, 10)]


def test_fetch_failure_reports_and_returns_1(capsys, tmp_path) -> None:
    session = RaisingSession(requests.Timeout("boom"))
    code = main(["--db", str(tmp_path / "x.sqlite")], session=session)  # type: ignore[arg-type]
    out, err = capsys.readouterr()

    assert code == 1
    assert out == ""
    assert err.startswith("booktracker: ")


def test_parse_failure_reports_and_returns_1(capsys, tmp_path) -> None:
    session = FakeSession(BAD_FIXTURE_NO_ID.read_bytes())
    code = main(["--db", str(tmp_path / "x.sqlite")], session=session)  # type: ignore[arg-type]
    out, err = capsys.readouterr()

    assert code == 1
    assert out == ""
    assert err.startswith("booktracker: ")


def test_empty_booklist(capsys, tmp_path) -> None:
    session = FakeSession(b"<html><body></body></html>")
    code = main(["--db", str(tmp_path / "x.sqlite")], session=session)  # type: ignore[arg-type]
    out, err = capsys.readouterr()
    assert code == 1
    assert out == ""
    assert err == "booktracker: No books were found in this page.\n"


@pytest.mark.parametrize(
    ("books", "expected"),
    [
        (
            [Book(123456, "An unusually long title", Decimal("12.50"), "In stock")],
            " 123456      12.50  In stock      An unusually long title",
        ),
        (
            [Book(1234567890, "Short Title", Decimal("12.50"), "In stock")],
            "1234567890      12.50  In stock      Short Title",
        ),
        (
            [Book(123456, "Short Title", Decimal("1200000.50"), "In stock")],
            " 123456  1200000.50  In stock      Short Title",
        ),
        (
            [Book(123456, "Short Title", Decimal("12.50"), "Totally In stock, man!")],
            " 123456      12.50  Totally In stock, man!  Short Title",
        ),
    ],
    ids=["long_title", "long_id", "long_price", "long_availability"],
)
def test_long_columns_table_width(books, expected) -> None:
    table = build_table(books)
    header, rule, row = table.splitlines()

    assert row == expected
    assert len(row) == len(rule)
