# Changelog

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
