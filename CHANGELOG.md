# Changelog

## 0.0.14

- Fixed `get_available_datasets()` missing datasets that are linked from the main research page only via a per-dataset collection landing page (e.g. `/research/cape`). Adds `india_cape` to the discovered dataset list.
- Fixed `read()` silently corrupting datasets whose feed has no title line before the CSV header (e.g. `india_cape`): the header row was being misread as a title and the first data row was being misread as the header, shifting every row and losing the header names. `_extract_table_chunk` now detects a title-less table by checking whether the first lines already look like a consistent CSV table, and `DESCR` falls back to the symbol name when no title is present.
- Fixed `_parse_index_if_dates` skipping date parsing entirely on pandas >= 3.0, where a text column/index defaults to a dedicated `str` dtype instead of `object`. The dtype check now uses `pandas.api.types.is_string_dtype`, which recognizes both, so dates keep parsing correctly regardless of pandas version.
- Pinned `pandas>=2.0` in `setup.py` (was unpinned) and raised `python_requires` to `>=3.8` to match - `pd.to_datetime(..., format="mixed")` in `_parse_index_if_dates` requires pandas 2.0+, which itself requires Python 3.8+, so the previous unpinned/`>=3.6` metadata could resolve to a combination that fails at import or at runtime. `README.md`'s Requirements section is updated to match.
- Refreshed the README's "Available Datasets" table against the live site: added `india_cape` and 15 other datasets that already existed but were missing, added three new category sections (Sector Portfolios, Universe Subsets, Fixed Income), and pointed to `get_available_datasets()` as the definitive list.
- Replaced the README's hand-written "Release Notes" prose with a pointer to `CHANGELOG.md`, so there's one place to keep in sync going forward instead of two.


## 0.0.12

- Fixed `get_available_datasets()` sending `Accept: application/json, text/csv` when fetching the HTML research page, which caused the server to return 406 Not Acceptable. The Accept header is now overridden to `text/html,application/xhtml+xml,*/*` for that request; all other headers (User-Agent, X-IndiaFactorLibrary-Version) continue to be sent via the existing `_get_response` path.

## 0.0.11

- Removed deprecated `pandas.read_csv(..., date_parser=...)` usage in favor of post-read index parsing compatible with newer pandas releases.
- Preserved existing index behavior as closely as possible: annual date-like indexes may still convert to `PeriodIndex`, while monthly date-like indexes remain `DatetimeIndex`.
- Added graceful HTTP 429 handling with bounded retries and `Retry-After` support.
- Reused the client request path for dataset discovery to improve timeout and status handling.
- Fixed `read()` for table-only payloads where no prose description is present.
- Standardized package versioning and license metadata.
- Added mocked tests covering parsing, retries, `DESCR` output, breakpoint datasets, and dataset discovery.
