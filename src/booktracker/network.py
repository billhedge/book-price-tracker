import requests


def fetch_page(session: requests.Session, url: str, timeout: float = 10) -> str:
    return ""  # placeholder
    # TODO: get with timeout; Timeout before ConnectionError -> FetchError ... from e
    # TODO: non-2xx -> FetchError
    # TODO: return response.content decoded as UTF-8; UnicodeDecodeError -> FetchError


# fetch_page: request with a timeout, catch Timeout before ConnectionError,
#  raise FetchError on non-2xx, decode the body as UTF-8, and turn UnicodeDecodeError
#  into FetchError.
