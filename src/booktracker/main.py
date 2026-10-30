import argparse

DEFAULT_URL = "https://books.toscrape.com/catalogue/category/books/horror_31/index.html"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="booktracker",
        description="Print the books on a books.toscrape.com listing page.",
    )
    parser.add_argument("url", nargs="?", default=DEFAULT_URL, help="listing page URL")
    parser.parse_args(argv)
    return 0
