from pathlib import Path

GOOD_FIXTURE = Path(__file__).parent / "fixtures/category-horror-page1.html"
BAD_FIXTURE_NO_ID = Path(__file__).parent / "fixtures/category-horror-page1-2nd-book-no-id.html"


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
