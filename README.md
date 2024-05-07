# IndiaFactorLibrary

Remote data access for Invespar's Data Library: Fama-French Factors, Momentum, and Low-Risk Factors for the Indian Market.

[![PyPI Version](https://img.shields.io/pypi/v/pandas-datareader.svg)](https://pypi.python.org/pypi/pandas-datareader/)
[![Code Coverage](https://codecov.io/gh/pydata/pandas-datareader/branch/master/graph/badge.svg)](https://codecov.io/gh/pydata/pandas-datareader)
[![Docs Latest](https://readthedocs.org/projects/pandas-datareader/badge/?version=latest)](https://pandas-datareader.readthedocs.io/en/latest/)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License](https://img.shields.io/pypi/l/pandas-datareader)](https://pypi.org/project/pandas-datareader/)

## Installation

Install using `pip`:

```shell
pip install indiafactorlibrary

## Usage

from indiafactorlibrary import IndiaFactorLibrary

# Create an instance of the library
ifl = IndiaFactorLibrary()

# Retrieve a list of available datasets
available_datasets = ifl.get_available_datasets()
print(available_datasets)

# Read a specific dataset
dataset = ifl.read('ff4')
print(dataset)

### Requirements

Using IndiaFactorLibrary package requires the following packages:

-   pandas>=1.5.3
-   lxml
-   requests>=2.19.0


## Documentation

### IndiaFactorLibrary Class (Invespar Data Library: Fama-French Factors, Momentum, and Low-Risk Factors for the Indian Market)

**Methods:**

- **read(symbol):**  
  Read data for a given symbol.

  - **Parameters:**  
    - `symbol` (str): The symbol for which to read the data.

  - **Returns:**  
    - `dict`: A dictionary of DataFrames parsed from the data.

- **get_available_datasets():**  
  Get the list of datasets available.

  - **Returns:**  
    - `list`: A list of valid data files for the IndiaFactorLibrary.

### Properties:

- **url:**  
  API URL for data access.


### Examples

To access the Fama-French dataset, you can call `read()` with the appropriate symbol like so:

```python
# Read the Fama-French 4-factor dataset
dataset = ifl.read('ff4')
print(dataset['DESCR'])
print(dataset[0])

