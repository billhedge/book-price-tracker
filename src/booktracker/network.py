import requests

from booktracker import exceptions as ex


def fetch_page(session: requests.Session, url: str, timeout: float = 10) -> str:
    try:
        response = session.get(url, timeout=timeout)
    except requests.RequestException as e:
        raise ex.FetchError(f"Failed to fetch {url}: {e}") from e
    if not 200 <= response.status_code < 300:
        raise ex.FetchError(f"HTTP {response.status_code} from {url}")
    try:
        return response.content.decode("utf-8")

    except UnicodeDecodeError as e:
        raise ex.FetchError(f"Failed to decode response from {url}") from e
