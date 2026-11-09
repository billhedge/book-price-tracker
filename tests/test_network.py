import pytest
import requests

import booktracker.exceptions as ex
from booktracker.network import fetch_page
from fakes import GOOD_FIXTURE, FakeSession, RaisingSession, _read


def test_success():
    session = FakeSession(GOOD_FIXTURE.read_bytes())
    html = fetch_page(session, "https://example.com")  # type: ignore[arg-type]

    assert session.calls == [("https://example.com", 10)]
    assert html == _read(GOOD_FIXTURE)


@pytest.mark.parametrize(
    ("raised"),
    [
        (requests.exceptions.Timeout),
        (requests.exceptions.ReadTimeout),
        (requests.exceptions.ConnectionError),
        (requests.exceptions.SSLError),
        (requests.exceptions.ConnectTimeout),  # the catch-order check
        (requests.exceptions.TooManyRedirects),
    ],
    ids=[
        "timeout",
        "read-timeout",
        "connection",
        "ssl",
        "connect-timeout",
        "redirects",
    ],
)
def test_transport_errors_are_translated(raised):
    original = raised("boom")
    session = RaisingSession(original)

    with pytest.raises(ex.FetchError) as exc_info:
        fetch_page(session, "https://example.com")  # type: ignore[arg-type]

    assert type(exc_info.value) is ex.FetchError
    assert exc_info.value.__cause__ is original


def test_non_utf8_body():
    session = FakeSession(content=b"\xff\xfe")

    with pytest.raises(ex.FetchError) as exc_info:
        fetch_page(session, "https://example.com")  # type: ignore[arg-type]

    assert type(exc_info.value) is ex.FetchError
    assert type(exc_info.value.__cause__) is UnicodeDecodeError


def test_404_is_translated_to_fetch_error():
    session = FakeSession(status_code=404)

    with pytest.raises(ex.FetchError) as exc_info:
        fetch_page(session, "https://example.com")  # type: ignore[arg-type]

    assert type(exc_info.value) is ex.FetchError
    assert exc_info.value.__cause__ is None


def test_500_is_translated_to_fetch_error():
    session = FakeSession(status_code=500)

    with pytest.raises(ex.FetchError) as exc_info:
        fetch_page(session, "https://example.com")  # type: ignore[arg-type]

    assert type(exc_info.value) is ex.FetchError
    assert exc_info.value.__cause__ is None
