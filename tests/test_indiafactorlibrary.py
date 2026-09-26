from unittest.mock import Mock

import pandas as pd
import pytest
import requests

import indiafactorlibrary.indiafactorlibrary as ifl_module
from indiafactorlibrary.indiafactorlibrary import IndiaFactorLibrary, RemoteDataError


class MockResponse:
    def __init__(self, text="", status_code=200, headers=None):
        self._text = text
        self.status_code = status_code
        self.headers = headers or {}
        self.content = text.encode("utf-8")

    @property
    def text(self):
        return self._text

    def raise_for_status(self):
        if self.status_code >= 400:
            error = requests.HTTPError(f"{self.status_code} error")
            error.response = self
            raise error


def make_client(get_side_effect):
    client = IndiaFactorLibrary()
    client.session = Mock()
    client.session.get.side_effect = get_side_effect
    return client


def test_read_parses_monthly_date_index():
    payload = (
        "Dataset description paragraph.\n\n"
        "Monthly Returns\n"
        "Dates,MF,SMB\n"
        "2004-10-31,1.2,-0.7\n"
        "2004-11-30,9.4,2.2\n"
    )
    client = make_client([MockResponse(payload)])

    dataset = client.read("ff4")

    assert isinstance(dataset[0].index, pd.DatetimeIndex)
    assert str(dataset[0].index[0].date()) == "2004-10-31"
    assert dataset[0].index.name == "Dates"


def test_parse_index_if_dates_handles_non_object_string_dtype():
    # pandas >= 3.0 defaults text columns/indexes to a dedicated "str"
    # dtype instead of "object". `pd.StringDtype` reproduces that same
    # "text but not object" shape on today's pandas, so this pins the
    # date-parsing guard's dtype check independent of which pandas is
    # actually installed.
    index = pd.Index(["2004-10-31", "2004-11-30"], dtype="string", name="Dates")
    assert index.dtype != object

    parsed = ifl_module._parse_index_if_dates(index)

    assert isinstance(parsed, pd.DatetimeIndex)
    assert parsed.name == "Dates"
    assert str(parsed[0].date()) == "2004-10-31"


def test_read_parses_dates_when_pandas_infers_string_dtype():
    # `future.infer_string` makes pandas < 3.0 behave like pandas' new
    # default: read_csv produces a "str"-dtype index instead of "object".
    # This runs the exact same payload as test_read_parses_monthly_date_index
    # end-to-end through client.read() under that setting, so the fix is
    # verified against the real pipeline, not just the helper function.
    payload = (
        "Dataset description paragraph.\n\n"
        "Monthly Returns\n"
        "Dates,MF,SMB\n"
        "2004-10-31,1.2,-0.7\n"
        "2004-11-30,9.4,2.2\n"
    )
    client = make_client([MockResponse(payload)])

    with pd.option_context("future.infer_string", True):
        dataset = client.read("ff4")

    assert isinstance(dataset[0].index, pd.DatetimeIndex)
    assert str(dataset[0].index[0].date()) == "2004-10-31"
    assert dataset[0].index.name == "Dates"


def test_read_parses_annual_index_to_period():
    payload = (
        "Dataset description paragraph.\n\n"
        "Annual Returns\n"
        "Years,MF,SMB\n"
        "2021,1.2,-0.7\n"
        "2022,9.4,2.2\n"
        "2023,3.1,1.4\n"
    )
    client = make_client([MockResponse(payload)])

    dataset = client.read("ff4")

    assert isinstance(dataset[0].index, pd.PeriodIndex)
    assert str(dataset[0].index[0]) == "2021"
    assert dataset[0].index.name == "Years"


def test_read_handles_mixed_date_like_index_gracefully():
    payload = (
        "Dataset description paragraph.\n\n"
        "Mixed Returns\n"
        "Dates,MF\n"
        "2004-10-31,1.2\n"
        "not-a-date,9.4\n"
        "2005,3.1\n"
    )
    client = make_client([MockResponse(payload)])

    dataset = client.read("ff4")

    assert isinstance(dataset[0].index, pd.DatetimeIndex)
    assert pd.isna(dataset[0].index[1])
    assert dataset[0].index.name == "Dates"


def test_breakpoint_dataset_keeps_multiindex_columns():
    payload = (
        "Breakpoint description.\n\n"
        "Breakpoints\n"
        "Date,Small,Small,Big,Big\n"
        "Date,Lo,Hi,Lo,Hi\n"
        "2023-01-31,1,2,3,4\n"
        "2023-02-28,5,6,7,8\n"
    )
    client = make_client([MockResponse(payload)])

    dataset = client.read("ff5_breakpoints")

    assert isinstance(dataset[0].columns, pd.MultiIndex)
    assert dataset[0].columns.tolist()[0] == ("Small", "Lo")


def test_read_handles_table_only_payload():
    payload = (
        "Monthly Returns\n"
        "Dates,MF,SMB\n"
        "2004-10-31,1.2,-0.7\n"
        "2004-11-30,9.4,2.2\n"
    )
    client = make_client([MockResponse(payload)])

    dataset = client.read("ff4")

    assert dataset["DESCR"] == "  0 : Monthly Returns (2 rows x 2 cols)"


def test_read_skips_empty_trailing_table_chunk():
    payload = (
        "Monthly Returns\n"
        "Dates,MF,SMB\n"
        "2004-10-31,1.2,-0.7\n"
        "2004-11-30,9.4,2.2\n\n"
    )
    client = make_client([MockResponse(payload)])

    dataset = client.read("ff4")

    assert [key for key in dataset if isinstance(key, int)] == [0]
    assert dataset[0].shape == (2, 2)


def test_read_skips_misclassified_notes_chunk():
    payload = (
        "The Conservative Portfolio and Equal Weighted 36 Month Volatility Ranked Decile Portfolios\n"
        "Dates,D_1,D_2,Conservative,Speculative,CMS\n"
        "2004-10-31,-0.8636,0.3145,0.3185,-1.2398,1.5582\n"
        "2004-11-30,6.8301,12.2641,11.4186,9.8991,1.5195\n\n"
        "NOTES: The portfolios are constructed at the end of each quarter.\n"
        "portfolios, the largest 1,000 stocks are included based on total market capitalisation are\n"
        "ranked based on the realised 36 months total return volatility.\n"
    )
    client = make_client([MockResponse(payload)])

    dataset = client.read("cms_portfolios")

    assert [key for key in dataset if isinstance(key, int)] == [0]
    assert dataset[0].shape == (2, 5)
    assert "NOTES:" in dataset["DESCR"]


def test_get_response_retries_rate_limit_with_retry_after(monkeypatch):
    sleep_calls = []
    monkeypatch.setattr(ifl_module.time, "sleep", sleep_calls.append)

    client = make_client(
        [
            MockResponse("slow down", status_code=429, headers={"Retry-After": "2"}),
            MockResponse("ok"),
        ]
    )

    response = client._get_response("https://example.com/data")

    assert response.status_code == 200
    assert sleep_calls == [2.0]


def test_get_response_merges_caller_headers():
    client = make_client([MockResponse("ok")])

    client._get_response("https://example.com/data", headers={"X-Test": "1"})

    kwargs = client.session.get.call_args.kwargs
    assert kwargs["headers"]["X-Test"] == "1"
    assert kwargs["headers"]["User-Agent"].startswith("IndiaFactorLibrary/")
    assert kwargs["headers"]["X-IndiaFactorLibrary-Version"]


def test_get_response_raises_after_persistent_rate_limit(monkeypatch):
    monkeypatch.setattr(ifl_module.time, "sleep", lambda _: None)

    client = make_client(
        [
            MockResponse("slow down", status_code=429, headers={"Retry-After": "1"}),
            MockResponse("slow down", status_code=429, headers={"Retry-After": "1"}),
            MockResponse("slow down", status_code=429, headers={"Retry-After": "1"}),
        ]
    )

    with pytest.raises(RemoteDataError, match="rate limit"):
        client._get_response("https://example.com/data")


def test_get_response_retries_server_errors(monkeypatch):
    sleep_calls = []
    monkeypatch.setattr(ifl_module.time, "sleep", sleep_calls.append)

    client = make_client(
        [
            MockResponse("temporary issue", status_code=503),
            MockResponse("ok"),
        ]
    )

    response = client._get_response("https://example.com/data")

    assert response.status_code == 200
    assert sleep_calls == [0.5]


def test_descr_combines_doc_chunks_and_table_descriptions():
    payload = (
        "First description chunk.\n\n"
        "Second description chunk.\n\n"
        "Monthly Returns\n"
        "Dates,MF\n"
        "2004-10-31,1.2\n"
    )
    client = make_client([MockResponse(payload)])

    dataset = client.read("ff4")

    assert dataset["DESCR"] == (
        "First description chunk. Second description chunk.\n\n"
        "  0 : Monthly Returns (1 rows x 1 cols)"
    )


def test_get_available_datasets_uses_html_response():
    html = """
    <html>
      <body>
        <a href="https://invespar.com/ajax/download/ff4">ff4</a>
        <a href="https://invespar.com/ajax/download/size_deciles">size</a>
        <a href="https://invespar.com/other">ignore</a>
      </body>
    </html>
    """
    client = make_client([MockResponse(html)])

    datasets = client._fetch_available_datasets()

    assert datasets == ["ff4", "size_deciles"]


def test_get_available_datasets_staticmethod_preserves_api(monkeypatch):
    monkeypatch.setattr(
        IndiaFactorLibrary,
        "_fetch_available_datasets",
        lambda self: ["ff4"],
    )

    assert IndiaFactorLibrary.get_available_datasets() == ["ff4"]


def test_get_available_datasets_follows_collection_landing_pages():
    # Mirrors the real research page: most datasets link straight to an
    # absolute ajax/download/ URL, but a newer dataset (India CAPE) instead
    # links to its own collection landing page under /research/, which in
    # turn links to the actual download with a site-relative href. Known
    # site furniture under /research/ (datasets index, methodology, and
    # in-page anchors) should not be crawled.
    main_html = """
    <html>
      <body>
        <a href="https://invespar.com/ajax/download/ff4">ff4</a>
        <a href="/research/cape">India CAPE</a>
        <a href="/research/datasets">All datasets</a>
        <a href="/research/methodology">Methodology</a>
        <a href="/research/#category-x">Category</a>
      </body>
    </html>
    """
    cape_html = """
    <html>
      <body>
        <a href="/ajax/download/india_cape">India CAPE data</a>
      </body>
    </html>
    """
    client = make_client([MockResponse(main_html), MockResponse(cape_html)])

    datasets = client._fetch_available_datasets()

    assert datasets == ["ff4", "india_cape"]
    called_urls = [call.args[0] for call in client.session.get.call_args_list]
    assert called_urls == [
        "https://invespar.com/research/",
        "https://invespar.com/research/cape",
    ]


def test_get_available_datasets_deduplicates_symbols_seen_twice():
    main_html = """
    <html>
      <body>
        <a href="https://invespar.com/ajax/download/india_cape">India CAPE</a>
        <a href="/research/cape">India CAPE landing page</a>
      </body>
    </html>
    """
    cape_html = """
    <html>
      <body>
        <a href="/ajax/download/india_cape">India CAPE data</a>
      </body>
    </html>
    """
    client = make_client([MockResponse(main_html), MockResponse(cape_html)])

    datasets = client._fetch_available_datasets()

    assert datasets == ["india_cape"]


def test_read_handles_headerless_csv_payload():
    # The India CAPE feed has no title line and no description prose - the
    # payload starts directly with the CSV header, unlike every other
    # dataset. This used to cause the header row to be misread as a title
    # and the first data row to be misread as the header.
    payload = (
        "Date,BSE Sensex CAPE 10,BSE Sensex CAPE 7,BSE Sensex CAPE 5\n"
        "1995-04-30,,,35.67\n"
        "1995-05-31,,,33.25\n"
    )
    client = make_client([MockResponse(payload)])

    dataset = client.read("india_cape")

    df = dataset[0]
    assert list(df.columns) == [
        "BSE Sensex CAPE 10",
        "BSE Sensex CAPE 7",
        "BSE Sensex CAPE 5",
    ]
    assert df.index.name == "Date"
    assert isinstance(df.index, pd.DatetimeIndex)
    assert df.shape == (2, 3)
    assert dataset["DESCR"] == "  0 : india_cape (2 rows x 3 cols)"
