from datetime import datetime, timezone
from io import StringIO
import time
from email.utils import parsedate_to_datetime
import re

import pandas as pd
import requests

from .version import __version__

_URL = "https://invespar.com/"
_URL_PREFIX = "ajax/download/"
_DEFAULT_TIMEOUT = 5
_MAX_RETRIES = 3
_MAX_BACKOFF_SECONDS = 5.0
_DATE_PARSE_SUCCESS_THRESHOLD = 0.6
_DATE_LIKE_PATTERN = re.compile(r"^\s*\d{4}([-/]\d{1,2}([-/]\d{1,2})?)?\s*$")


def _normalize_index_values(index):
    return pd.Series(index, dtype="object").map(
        lambda value: value.strip() if isinstance(value, str) else value
    )


def _is_year_like_numeric_index(index):
    if not pd.api.types.is_integer_dtype(index.dtype):
        return False
    if len(index) == 0:
        return False
    return bool(((index >= 1000) & (index <= 2999)).all())


def _looks_date_like(parsed_index, original_values):
    non_empty_mask = original_values.notna() & (original_values != "")
    candidate_count = int(non_empty_mask.sum())
    if candidate_count == 0:
        return False
    parsed_count = int(parsed_index[non_empty_mask].notna().sum())
    return parsed_count / candidate_count >= _DATE_PARSE_SUCCESS_THRESHOLD


def _parse_index_if_dates(index):
    if not isinstance(index, pd.Index):
        return index

    # is_string_dtype (rather than dtype == object) is what keeps this
    # working on pandas >= 3.0, where a text column/index defaults to a
    # dedicated "str" dtype instead of "object"; is_string_dtype recognizes
    # both, while still returning False for a numeric index.
    if not pd.api.types.is_string_dtype(index.dtype) and not _is_year_like_numeric_index(index):
        return index

    original_name = index.name
    normalized_values = _normalize_index_values(index)
    parsed_index = pd.Series(pd.NaT, index=normalized_values.index, dtype="datetime64[ns]")

    strict_daily = pd.to_datetime(normalized_values, format="%Y-%m-%d", errors="coerce")
    parsed_index = strict_daily

    unresolved = parsed_index.isna()
    if unresolved.any():
        parsed_index.loc[unresolved] = pd.to_datetime(
            normalized_values.loc[unresolved], format="%Y", errors="coerce"
        )

    unresolved = parsed_index.isna()
    if unresolved.any():
        date_like_mask = normalized_values.loc[unresolved].map(
            lambda value: isinstance(value, str) and bool(_DATE_LIKE_PATTERN.match(value))
        )
        if date_like_mask.any():
            fallback_values = normalized_values.loc[unresolved][date_like_mask]
            parsed_index.loc[fallback_values.index] = pd.to_datetime(
                fallback_values, errors="coerce", format="mixed"
            )

    if not _looks_date_like(parsed_index, normalized_values):
        return index

    parsed = pd.DatetimeIndex(parsed_index, name=original_name)
    return parsed


def convert_index_to_period(df):
    inferred_freq = df.index.inferred_freq
    if inferred_freq is not None:
        if inferred_freq.startswith(("A", "Y")):
            return df.to_period("Y")
    return df

class RemoteDataError(IOError):
    pass

class IndiaFactorLibrary:
    """
    Get data for the given name from the Invespar India Fama/French data library.

    Annual datasets may use a pandas.PeriodIndex when the frequency can be
    inferred reliably. Other datasets use a pandas.DatetimeIndex when the
    index is clearly date-like.
    """

    def __init__(self):
        self.session = requests.Session()

    def _get_response(self, url, params=None, headers=None):
        default_headers = {
            "User-Agent": (
                f"IndiaFactorLibrary/{__version__} "
                "(+https://invespar.com/research/)"
            ),
            "Accept": "application/json, text/csv",
            "X-IndiaFactorLibrary-Version": __version__,
        }
        request_headers = {**default_headers, **(headers or {})}

        for attempt in range(_MAX_RETRIES):
            try:
                response = self.session.get(
                    url,
                    params=params,
                    headers=request_headers,
                    timeout=_DEFAULT_TIMEOUT,
                )
                response.raise_for_status()
                return response
            except requests.HTTPError as e:
                response = e.response
                status_code = response.status_code if response is not None else None

                if status_code == 429:
                    if attempt < _MAX_RETRIES - 1:
                        time.sleep(self._get_retry_delay(response, attempt))
                        continue
                    raise RemoteDataError(
                        f"Persistent rate limit while retrieving {url} "
                        f"(status 429 after {_MAX_RETRIES} attempts)"
                    )

                if status_code in [500, 502, 503, 504]:
                    if attempt < _MAX_RETRIES - 1:
                        time.sleep(min(0.5 * (2**attempt), _MAX_BACKOFF_SECONDS))
                        continue
                    raise RemoteDataError(
                        f"HTTP error occurred while retrieving {url}: "
                        f"status {status_code} after {_MAX_RETRIES} attempts"
                    )

                raise RemoteDataError(f"HTTP error occurred while retrieving {url}: {e}")
            except requests.RequestException as e:
                if attempt < _MAX_RETRIES - 1:
                    time.sleep(min(0.5 * (2**attempt), _MAX_BACKOFF_SECONDS))
                    continue
                raise RemoteDataError(f"Failed to connect to {url}: {str(e)}")

        raise RemoteDataError(f"Failed to retrieve data after {_MAX_RETRIES} attempts")

    @staticmethod
    def _get_retry_delay(response, attempt):
        retry_after = response.headers.get("Retry-After") if response is not None else None
        if retry_after:
            try:
                return min(float(retry_after), _MAX_BACKOFF_SECONDS)
            except ValueError:
                try:
                    retry_after_dt = parsedate_to_datetime(retry_after)
                    now = datetime.now(tz=retry_after_dt.tzinfo or timezone.utc)
                    delay = (retry_after_dt - now).total_seconds()
                    return max(0.0, min(delay, _MAX_BACKOFF_SECONDS))
                except (TypeError, ValueError, OverflowError):
                    pass
        return min(0.5 * (2**attempt), _MAX_BACKOFF_SECONDS)

    def _read_file(self, url):
        return self._get_response(url).content.decode("utf-8")

    def build_url(self, symbol):
        """
        Construct the full URL for a given symbol.

        Parameters:
        symbol : str
            The symbol for which to construct the URL.

        Returns:
        str : The fully constructed URL.
        """
        return _URL + _URL_PREFIX + symbol

    @staticmethod
    def analyze_chunk_content(chunk):
        lines = [line.strip() for line in chunk.splitlines() if line.strip()]
        if len(lines) >= 2:
            sample_lines = lines[:3]
            comma_counts = [line.count(",") for line in sample_lines]
            if comma_counts[1] > 0 and max(comma_counts) >= 1:
                return False

        cleaned_chunk = chunk.replace("\r\n", " ").strip()
        numeric_count = sum(c.isnumeric() for c in cleaned_chunk)
        alpha_count = sum(c.isalpha() for c in cleaned_chunk)
        return alpha_count > numeric_count

    @staticmethod
    def _looks_like_headerless_table(lines):
        """
        True when a chunk's own first line is already a CSV header, i.e.
        there is no separate title line above it. Some datasets (e.g. the
        India CAPE feed) are served as bare CSV with no title or
        description at all, unlike the usual "Title\\nheader,row\\ndata"
        shape. We detect this by checking that the first few lines share
        the same comma count (a title line reads as prose and normally
        has none), the same signal `analyze_chunk_content` uses.
        """
        sample = lines[:3]
        if len(sample) < 2:
            return False
        comma_counts = [line.count(",") for line in sample]
        if comma_counts[0] < 1:
            return False
        return len(set(comma_counts)) == 1

    @staticmethod
    def _extract_table_chunk(chunk):
        stripped_chunk = chunk.strip()
        if not stripped_chunk or "\n" not in stripped_chunk:
            return None

        all_lines = [line.strip() for line in stripped_chunk.splitlines() if line.strip()]
        if len(all_lines) < 2:
            return None

        if IndiaFactorLibrary._looks_like_headerless_table(all_lines):
            title, table_lines = None, all_lines
        else:
            title, table_text = stripped_chunk.split("\n", 1)
            table_lines = [line.strip() for line in table_text.splitlines() if line.strip()]
            if len(table_lines) < 2:
                return None
            title = title.strip()

        header_commas = table_lines[0].count(",")
        first_row_commas = table_lines[1].count(",")
        if header_commas < 1 or first_row_commas < 1:
            return None

        return title, "\n".join(table_lines)

    @staticmethod
    def _read_csv_table(table_text, params):
        df = pd.read_csv(StringIO(table_text), **params)
        idx_name = df.index.name
        df.index = _parse_index_if_dates(df.index)
        df.index.name = idx_name
        try:
            df = convert_index_to_period(df)
            df.index.name = idx_name
        except Exception:
            pass
        return df

    def read(self, symbol):
        """
        Read data for a given symbol from the constructed URL.

        Parameters:
        symbol : str
            The symbol for which to read the data.

        Returns:
        dict : A dictionary of DataFrames parsed from the data.
        """
        if symbol.find("_breakpoints") == -1:
            params = {
                "index_col": 0,
            }
        else:
            params = {
                "header": [0, 1],
                "index_col": 0,
            }
        url = self.build_url(symbol)
        data = self._read_file(url)
        doc_chunks, tables = [], []

        for chunk in data.split("\n\n"):
            if self.analyze_chunk_content(chunk) and len(chunk) < 1600:
                doc_chunks.append(chunk.replace("\r\n", " ").strip())
            else:
                tables.append(chunk)

        datasets, table_desc = {}, []
        for src in tables:
            extracted_chunk = self._extract_table_chunk(src)
            if extracted_chunk is None:
                cleaned_chunk = src.replace("\r\n", " ").strip()
                if cleaned_chunk and len(cleaned_chunk) < 1600:
                    doc_chunks.append(cleaned_chunk)
                continue

            title, table_text = extracted_chunk
            if title is None:
                # No title line was present in the source (e.g. a bare CSV
                # feed with no description) - fall back to the symbol so
                # DESCR still identifies which table this is.
                title = symbol
            df = self._read_csv_table(table_text, params)
            if df.empty and len(df.columns) == 0:
                continue

            datasets[len(datasets)] = df

            shape = "({} rows x {} cols)".format(*df.shape)
            table_desc.append(f"{title} {shape}".strip())

        descr = ""
        if doc_chunks:
            descr = " ".join(doc_chunks).replace(2 * " ", " ") + "\n\n"
        table_descr = map(lambda x: "{:3} : {}".format(*x), enumerate(table_desc))
        datasets["DESCR"] = descr + "\n".join(table_descr)

        return datasets

    # Sub-pages directly under /research/ that are known site furniture
    # rather than a per-dataset collection landing page (like /research/cape)
    # and so should not be crawled for download links.
    _NON_COLLECTION_RESEARCH_SLUGS = {"datasets", "methodology"}

    def _fetch_html(self, url, document_fromstring):
        response = self._get_response(
            url, headers={"Accept": "text/html,application/xhtml+xml,*/*"}
        )
        root = document_fromstring(response.content, base_url=url)
        root.make_links_absolute()
        return [e.attrib["href"] for e in root.findall(".//a") if "href" in e.attrib]

    def _fetch_available_datasets(self):
        """
        Get the list of datasets available from the Fama/French data library.

        Most datasets are linked directly from the main research page as
        absolute ajax/download/ URLs. Some newer datasets (e.g. India CAPE)
        instead sit behind their own collection landing page
        (/research/<slug>) and are linked from there with a site-relative
        href, so those pages are followed one level deep as well.

        Returns
        -------
        datasets : list
            A list of valid inputs for get_data_famafrench.
        """
        try:
            from lxml.html import document_fromstring
        except ImportError as exc:
            raise ImportError(
                "Please install lxml if you want to use the "
                "get_available_datasets function"
            ) from exc

        research_url = _URL + "research/"
        download_prefix = _URL + _URL_PREFIX

        def download_symbols(hrefs):
            return [h[len(download_prefix):] for h in hrefs if h.startswith(download_prefix)]

        def collection_pages(hrefs):
            pages = set()
            for href in hrefs:
                path_part = href.split("#", 1)[0]
                if not path_part.startswith(research_url) or path_part == research_url:
                    continue
                remainder = path_part[len(research_url):].strip("/")
                if not remainder or "/" in remainder:
                    continue
                if remainder in self._NON_COLLECTION_RESEARCH_SLUGS:
                    continue
                pages.add(path_part.rstrip("/"))
            return sorted(pages)

        main_hrefs = self._fetch_html(research_url, document_fromstring)
        symbols = download_symbols(main_hrefs)

        for page_url in collection_pages(main_hrefs):
            try:
                sub_hrefs = self._fetch_html(page_url, document_fromstring)
            except RemoteDataError:
                continue
            symbols.extend(download_symbols(sub_hrefs))

        seen = set()
        ordered = []
        for symbol in symbols:
            if symbol not in seen:
                seen.add(symbol)
                ordered.append(symbol)
        return ordered

    @staticmethod
    def get_available_datasets():
        return IndiaFactorLibrary()._fetch_available_datasets()
