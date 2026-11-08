from decimal import Decimal

import requests

from booktracker.main import DEFAULT_URL, GAP, Book, build_table, main
from fakes import BAD_FIXTURE_NO_ID, GOOD_FIXTURE, FakeSession, RaisingSession


def test_success_prints_table(capsys) -> None:
    session = FakeSession(GOOD_FIXTURE.read_bytes())

    code = main([], session=session)  # type: ignore[arg-type]

    out, err = capsys.readouterr()
    lines = out.splitlines()
    assert code == 0
    assert len(lines) == 19  # header + rule + books
    assert err == ""
    assert session.calls == [(DEFAULT_URL, 10)]
    assert lines[2] == "    925      39.25  In stock      Security"
    assert any("Security" in row for row in lines)


def test_custom_url_is_fetched(capsys) -> None:
    session = FakeSession(GOOD_FIXTURE.read_bytes())
    url = "https://example.com/books"
    code = main([url], session=session)  # type: ignore[arg-type]
    out, err = capsys.readouterr()

    assert code == 0
    assert out
    assert err == ""
    assert session.calls == [(url, 10)]


def test_fetch_failure_reports_and_returns_1(capsys) -> None:
    session = RaisingSession(requests.Timeout("boom"))
    code = main([], session=session)  # type: ignore[arg-type]
    out, err = capsys.readouterr()

    assert code == 1
    assert out == ""
    assert err.startswith("booktracker: ")


def test_parse_failure_reports_and_returns_1(capsys) -> None:
    session = FakeSession(BAD_FIXTURE_NO_ID.read_bytes())
    code = main([], session=session)  # type: ignore[arg-type]
    out, err = capsys.readouterr()

    assert code == 1
    assert out == ""
    assert err.startswith("booktracker: ")


def test_empty_booklist(capsys) -> None:
    session = FakeSession(b"<html><body></body></html>")
    code = main([], session=session)  # type: ignore[arg-type]
    out, err = capsys.readouterr()
    assert code == 1
    assert out == ""
    assert err == "booktracker: No books were found in this page.\n"


def _cells_from_row(row: str, columns: tuple[tuple[str, int], ...]) -> list[str]:
    cells = []
    start = 0

    for index, (_, width) in enumerate(columns):
        cells.append(row[start : start + width].strip())
        start += width
        if index < len(columns) - 1:
            start += len(GAP)

    return cells


def test_long_title_table_width() -> None:
    table = build_table([Book(123456, "An unusually long title", Decimal("12.50"), "In stock")])
    header, rule, row = table.splitlines()

    cells = _cells_from_row(
        row,
        columns=(
            ("Book ID", 7),
            ("Price (£)", 9),
            ("Availability", 12),
            ("Title", 23),
        ),
    )

    assert len(row) == len(rule)  # this row matches the rule's width
    assert cells[0].endswith("123456")
    assert cells[1].endswith("12.50")
    assert cells[2].startswith("In stock")
    assert cells[3].startswith("An unusually long title")


def test_long_id_table_width() -> None:
    table = build_table([Book(1234567890, "Short Title", Decimal("12.50"), "In stock")])
    header, rule, row = table.splitlines()

    cells = _cells_from_row(
        row,
        columns=(
            ("Book ID", 10),
            ("Price (£)", 9),
            ("Availability", 12),
            ("Title", 11),
        ),
    )

    assert len(row) == len(rule)  # this row matches the rule's width
    assert cells[0].endswith("1234567890")  # Book ID: right-aligned
    assert cells[1].endswith("12.50")  # Price: right-aligned
    assert cells[2].startswith("In stock")  # Availability: left-aligned
    assert cells[3].startswith("Short Title")  # Title: left-aligned


def test_long_price_table_width() -> None:
    table = build_table([Book(1234567, "Short Title", Decimal("1200000.50"), "In stock")])
    header, rule, row = table.splitlines()

    cells = _cells_from_row(
        row,
        columns=(
            ("Book ID", 7),
            ("Price (£)", 10),
            ("Availability", 12),
            ("Title", 11),
        ),
    )

    assert len(row) == len(rule)  # this row matches the rule's width
    assert cells[0].endswith("1234567")  # Book ID: right-aligned
    assert cells[1].endswith("1200000.50")  # Price: right-aligned
    assert cells[2].startswith("In stock")  # Availability: left-aligned
    assert cells[3].startswith("Short Title")  # Title: left-aligned


def test_long_availability_table_width() -> None:
    table = build_table([Book(1234567, "Short Title", Decimal("12.50"), "Totally In stock, man!")])
    header, rule, row = table.splitlines()

    cells = _cells_from_row(
        row,
        columns=(
            ("Book ID", 7),
            ("Price (£)", 9),
            ("Availability", 22),
            ("Title", 11),
        ),
    )

    assert len(row) == len(rule)  # this row matches the rule's width
    assert cells[0].endswith("1234567")  # Book ID: right-aligned
    assert cells[1].endswith("12.50")  # Price: right-aligned
    assert cells[2].startswith("Totally In stock, man!")  # Availability: left-aligned
    assert cells[3].startswith("Short Title")  # Title: left-aligned
