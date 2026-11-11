import pytest

import fakes
from booktracker.changes import check_changes
from booktracker.storage import connect, save_scrape

URL = "https://example.com"


@pytest.mark.parametrize(
    ("scrapes", "expected"),
    [
        ([fakes.BOOKS1, fakes.BOOKS1], [f"No price changes for {URL}."]),
        ([fakes.BOOKS1, fakes.BOOKS_UP], ["430 59.21 -> 75.00 Title 3"]),
        ([fakes.BOOKS1, fakes.BOOKS_DOWN], ["111 14.95 -> 5.99 Title 2"]),
        ([fakes.BOOKS1, fakes.BOOKS_DECIMAL], [f"No price changes for {URL}."]),
        ([fakes.BOOKS1], [f"Need more than one scrape for {URL} to compare."]),
        ([fakes.BOOKS1, fakes.BOOKS_PLUS_ONE], [f"No price changes for {URL}."]),
        (
            [fakes.BOOKS1, fakes.BOOKS_MULTIPLE_CHANGES],
            ["111 14.95 -> 5.99 Title 2", "430 59.21 -> 75.00 Title 3"],
        ),
        (
            [fakes.BOOKS1, fakes.BOOKS_PLUS_ONE, fakes.BOOKS_THIRD_SCRAPE],
            ["999 99.99 -> 99.90 Title 4"],
        ),
    ],
    ids=[
        "no_change",
        "one_price_up",
        "one_price_down",
        "decimal_check",
        "one_scrape",
        "one_new_book",
        "results_in_id_order",
        "third_scrape_with_change",
    ],
)
def test_changes(scrapes, expected):
    cnn = connect(":memory:")
    for i, scrape in enumerate(scrapes):
        save_scrape(cnn, URL, f"2026-11-10T0{i}:00:00+00:00", scrape)

    check = check_changes(cnn, URL)

    assert check == expected
