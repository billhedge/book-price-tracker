class AppError(Exception):  # Base exception
    """Base for every expected failure. main() catches this and returns 1."""


class FetchError(AppError):
    """timeout, connection, non-2xx, body not UTF-8"""


class ParseError(AppError):
    """the page isn't shaped the way we expect"""


class StorageError(AppError):
    """unable to store data"""
