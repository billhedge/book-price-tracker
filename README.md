# booktracker

A command-line tool that connects to a single page on books.toscrape.com, a demo website created for scraping practice, parses the page, and prints out a table with the information representing books on that page. The displayed data includes ID, price (in GBP), availability, and title. Built as a learning project covering Python web scraping, error handling, and offline testing.

Table output:

```bash
booktracker
```
```text
Book ID  Price (£)  Availability  Title
-------  ---------  ------------  ------------------------------------------------
    925      39.25  In stock      Security
    809      21.36  In stock      Follow You Home
    756      23.40  In stock      The Loney
    726      10.56  In stock      Pet Sematary
    686      40.12  In stock      Doctor Sleep (The Shining #2)
    628      36.97  In stock      Psycho: Sanitarium (Psycho #1.5)
    614      48.64  In stock      Can You Keep a Secret? (Fear Street Relaunch #4)
    390      23.37  In stock      Red Dragon (Hannibal Lecter #1)
...
```

## Features

- Gathers book information scraped from the HTML of a single listing page
- Prints an aligned table
- Reports errors in one line with exit code `1`

## Install

Requires Python 3.10 or newer.

```bash
git clone https://github.com/billhedge/book-price-tracker.git
cd book-price-tracker
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
pip install -e .
```
On Windows PowerShell, if activation fails with "running scripts is disabled", run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once and try again.

## Usage

Usage: `booktracker [URL]`

```bash
booktracker https://books.toscrape.com/catalogue/category/books/art_25/index.html
booktracker https://books.toscrape.com/catalogue/category/books/historical_42/index.html
booktracker https://books.toscrape.com/catalogue/category/books/crime_51/index.html
```
Exit codes: `0` success, `1` application error. Check the last one with `echo $?` (PowerShell: `echo $LASTEXITCODE`).

The application only reads the single URL passed to it (the first page of the *Horror* category is used by default if no URL is passed). If you want more pages of a category to be parsed, you must submit multiple requests using the complete URL to each page. 

Note that `python -m booktracker https://books.toscrape.com/catalogue/category/books/art_25/index.html` works, too!

## Development

Set up the environment as in [Install](#install), but instead of the last step install the development tools too:

```bash
pip install -e ".[dev]"
```

Run the checks before committing:

```bash
ruff check .
ruff format --check .
mypy
pytest
```

Coverage testing:

```bash
pytest --cov=booktracker --cov-report=term-missing
pytest --cov=booktracker --cov-branch --cov-report=term-missing   # include branches
pytest --cov=booktracker --cov-report=html                        # then open htmlcov/index.html
```

CI runs the same checks on Python 3.10 to 3.13.

## Design notes

- **Error handling.** Every expected failure derives from `AppError`. `main()` catches it and prints an error message to `stderr`, without the traceback, and exits with code `1`. Anything that isn't an `AppError` is a bug and is not caught, so the traceback will show. There are two groups:
  - `FetchError`: the page could not be fetched (network errors, HTTP status, and non-UTF-8 body). Trying the request again later may work for network errors.
  - `ParseError`: the page structure could not be parsed due to unexpected changes such as a missing element, a link without an ID, a price that will not parse, or a page with no books.
- **Injectable HTTP client.** The session is injected in `main(argv, session)` and `fetch_page(session, url)`. Tests pass in `FakeSession`s and nothing is patched.
- **Retries and timeouts.** Every request has a 10-second timeout. There are no retries.
- **Data notes.** 
   - The book ID comes from the number at the end of the product link.
   - Titles come from the link's `title` attribute, because the link text is truncated.
   - Prices are `Decimal`, not `float`.
   - HTTP bodies are explicitly decoded as UTF-8. Stdout is set to UTF-8, so that output is the same in both Windows and Linux.
- **Offline tests with real data.** Fixtures are responses captured from the live website, via `scripts/capture-fixture.ps1`; the malformed ones used for failure paths are edited copies (one defect per file as noted in an HTML comment at the top of each). The suite runs without a network connection.
- **Output.** Column widths come from the widest of data or the respective headers, so the table stays aligned whatever the length of the data in each column. Stdout carries only results and stderr carries errors, so piping works.

## Roadmap

- Milestone 2: store each scrape in SQLite.
- Milestone 3: compare the latest scrape with the previous one and print price changes.


## Data and attribution

Data obtained from [books.toscrape.com](https://books.toscrape.com), a demo website that provides web pages for scraping practice. From the website: "Prices and ratings here were randomly assigned and have no real meaning."


## License

MIT. See [LICENSE](LICENSE).
