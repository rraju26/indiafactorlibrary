import datetime as dt
import requests
from io import StringIO
import pandas as pd

_URL = "https://invespar.com/"
_URL_PREFIX = "ajax/download/"

def _parse_date_famafrench(x):
    try:
        x = x.strip()
    except:
        x = x
        #print(x)
    try:
        if '-' in x:  # Likely a complete date
            return dt.datetime.strptime(x, "%Y-%m-%d")
        else:
            return dt.datetime.strptime(x, "%Y")  # Just a year
    except ValueError:
        return pd.to_datetime(x, errors='coerce')  # Use pandas to parse or return NaT on error

def convert_index_to_period(df):
    inferred_freq = df.index.inferred_freq
    if inferred_freq is not None:
        # Only convert if frequency can be reliably inferred
        if inferred_freq.startswith('A'):
            return df.to_period('A')  # Convert to annual period
    return df  # Return original DataFrame if no inference possible

class RemoteDataError(IOError):
    pass

class IndiaFactorLibrary:
    """
    Get data for the given name from the Invespar India Fama/French data library.

    For annual and monthly data, index is a pandas.PeriodIndex, otherwise
    it's a pandas.DatetimeIndex.
    """

    def __init__(self):
        self.session = requests.Session()  # Persistent session
    
    def _get_response(self, url, params=None, headers=None):
        retries = 3
        for attempt in range(retries):
            try:
                response = self.session.get(url, params=params, headers=headers, timeout=5)
                response.raise_for_status()  # Will raise an HTTPError for bad responses
                return response
            except requests.HTTPError as e:
                if e.response.status_code in [500, 502, 503, 504]:
                    if attempt < retries - 1:  # Retry on server errors
                        continue
                raise RemoteDataError(f"HTTP error occurred: {e}")  # Reraise for non-retry cases or client errors
            except requests.RequestException as e:
                raise RemoteDataError(f"Failed to connect to {url}: {str(e)}")
        raise RemoteDataError(f"Failed to retrieve data after {retries} attempts")
  
    def _read_file(self, url):
        return self._get_response(url).content.decode('utf-8')
    
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
        cleaned_chunk = chunk.replace("\r\n", " ").strip()
        numeric_count = sum(c.isnumeric() for c in cleaned_chunk)
        alpha_count = sum(c.isalpha() for c in cleaned_chunk)
        if alpha_count > numeric_count:
            return True
        else:
            return False

    def read(self, symbol):
        """
        Read data for a given symbol from the constructed URL.

        Parameters:
        symbol : str
            The symbol for which to read the data.

        Returns:
        dict : A dictionary of DataFrames parsed from the data.
        """
        if symbol.find('_breakpoints')==-1: #not breakpoint
            params = {
                "index_col": 0,
                "parse_dates": [0],
                "date_parser": _parse_date_famafrench,
            }
        else: #has breakpoints which has multiiindex columns
            params = {
                "header": [0, 1],  # Use the first two rows as headers
                "index_col": 0,  # Set the first column as the index, adjust if necessary
                "parse_dates": [0],  
                "date_parser": _parse_date_famafrench
            }
        url = self.build_url(symbol)
        data = self._read_file(url)
        datasets = {}
        doc_chunks, tables = [], []

        for chunk in data.split("\n\n"):
            if self.analyze_chunk_content(chunk) and len(chunk) < 1600:
                doc_chunks.append(chunk.replace("\r\n", " ").strip())
            else:
                tables.append(chunk)

        datasets, table_desc = {}, []
        for i, src in enumerate(tables):
            title_pos = src.find('\n')
            title = src[:title_pos].strip()
            start = title_pos+1
            df = pd.read_csv(StringIO(src[start:]), **params)
            try:
                idx_name = df.index.name
                df = convert_index_to_period(df)
                df.index.name = idx_name
            except Exception:
                pass
            df = df#.truncate(start, self.end)
            datasets[i] = df
    
            shape = "({} rows x {} cols)".format(*df.shape)
            table_desc.append(f"{title} {shape}".strip())
    
        if doc_chunks:
            descr = " ".join(doc_chunks).replace(2 * " ", " ") + "\n\n"
        table_descr = map(lambda x: "{:3} : {}".format(*x), enumerate(table_desc))
        datasets["DESCR"] = descr + "\n".join(table_descr)
        
        return datasets
    
    @staticmethod
    def get_available_datasets():
        """
        Get the list of datasets available from the Fama/French data library.
 
        Returns
        -------
        datasets : list
            A list of valid inputs for get_data_famafrench.
        """
        response = requests.get(_URL + 'research/')
        try:
            from lxml.html import document_fromstring
        except ImportError as exc:
            raise ImportError(
                "Please install lxml if you want to use the "
                "get_available_datasets function"
            ) from exc
        root = document_fromstring(response.content)
    
        datasets = [e.attrib["href"] for e in root.findall(".//a") if "href" in e.attrib]
        datasets = [ds for ds in datasets if ds.startswith(_URL + _URL_PREFIX)]
        return [ds[len(_URL + _URL_PREFIX):] for ds in datasets]
