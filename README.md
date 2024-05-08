# IndiaFactorLibrary

The **IndiaFactorLibrary** is a python package for remote data access for Invespar's Data Library: Fama-French Factors, Momentum, and Low-Risk Factors for the Indian Market.

## Key Features
- Retrieve well-structured data sets with minimal code.
- Access both monthly and annual data.
- Focus on factors relevant to the Indian market.

## Installation

To install IndiaFactorLibrary, ensure you have Python 3.6 or later and use `pip`:

```shell
pip install indiafactorlibrary
```
## Requirements

Using IndiaFactorLibrary package requires the following packages:

-   Python 3.6 or later
-   pandas>=1.5.3
-   lxml
-   requests>=2.19.0


## Usage
```python
from indiafactorlibrary import IndiaFactorLibrary

# Create an instance of the library
ifl = IndiaFactorLibrary()

# Retrieve a list of available datasets
available_datasets = ifl.get_available_datasets()
print(available_datasets)
```

## Available Datasets

The following datasets are available through the **IndiaFactorLibrary** as of April 2024. This list is automatically updated, and users can access each dataset by passing the relevant symbol to the `read` method.

| Symbol                | Description                                           |
|-----------------------|-------------------------------------------------------|
| **ff4**               | Fama-French 4 factors                                 |
| **ff6**               | Fama-French 6 factors                                 |
| **size_value_portfolios** | 6 portfolios sorted by size and value (2x3)       |
| **size_op_portfolios** | 6 portfolios sorted by size and operating profitability (2x3) |
| **size_inv_portfolios** | 6 portfolios sorted by size and investment (2x3)    |
| **size_mom_portfolios** | 6 portfolios sorted by size and momentum (2x3)      |
| **size_deciles**      | 10 portfolios sorted by size                          |
| **btm_deciles**       | 10 portfolios sorted by book-to-market ratio          |
| **op_deciles**        | 10 portfolios sorted by operating profitability       |
| **in_deciles**        | 10 portfolios sorted by investment                    |
| **mom_deciles**       | 10 portfolios sorted by momentum                      |
| **vol_deciles**       | 10 portfolios sorted by volatility                    |
| **size_btm_5x5**      | 5x5 portfolios sorted by size and book-to-market ratio |
| **size_op_5x5**       | 5x5 portfolios sorted by size and operating profitability |
| **size_inv_5x5**      | 5x5 portfolios sorted by size and investment          |
| **size_mom_5x5**      | 5x5 portfolios sorted by size and momentum            |
| **size_vol_5x5**      | 5x5 portfolios sorted by size and volatility          |
| **low_risk_factors**  | Low-risk factors                                      |
| **low_risk_factors_vol** | Low-risk factors based on realized volatility      |
| **low_risk_factors_bab_fp** | Betting Against Beta (Frazzini-Pedersen methodology) |
| **low_risk_factors_bab_ff** | Ex-ante BAB methodology (Fama-French 2x3 construction) |
| **low_risk_factors_bab_capm** | BAB using CAPM Beta (FF 2x3 construction)     |
| **low_risk_factors_ivol** | Low-risk factors using idiosyncratic volatility   |
| **f2_week_high**      | 52-week high effect                                   |
| **cms_portfolios**    | CMS (Conservative Formula) portfolios                 |
| **ff5_breakpoints**   | Breakpoints for Fama-French 5 factors                 |
| **mom_breakpoints**   | Breakpoints for momentum factors                      |
| **lovol_breakpoints** | Breakpoints for low-volatility factors                |

Note:
This list is updated automatically, and the datasets available may change over time as new data is added or removed.

### Accessing Datasets

You can retrieve and analyze each dataset by calling the `read` method with the appropriate symbol:

```python
from indiafactorlibrary import IndiaFactorLibrary

# Initialize the library
ifl = IndiaFactorLibrary()

# Read the Fama-French 4 factors dataset
dataset = ifl.read('ff4')

# Print the dataset description and an example DataFrame
print(dataset['DESCR'])
print(dataset[0].head())
```

The `read` method retrieves a dataset and returns it as a dictionary of DataFrames. Here's a detailed explanation of the output:

```python
{0:                 MF     SMB     HML     WML      RF     MKT
 Dates                                                     
 2004-10-31  1.2168 -0.7685 -2.0792  2.7795  0.3877  1.6045
 2004-11-30  9.4784  2.2380  1.0583  1.6852  0.4361  9.9145
 ...         ...     ...     ...     ...     ...     ...
 2024-04-30  4.1476  7.2296  3.4824  3.0271  0.5466  4.6942

 [235 rows x 6 columns],
 1:           MF    SMB    HML    WML    RF    MKT
 Years                                         
 2005   34.40   9.26  -5.23  18.29  5.46  41.56
 2006   29.29  -6.02  -4.24  26.63  6.40  37.40
 ...     ...     ...     ...     ...     ...    ...
 2023   20.91  17.96  29.37  15.21  6.80  29.00,
 'DESCR': '"This file contains value-weighted monthly and annual returns for long-short factors. Annual factors are geometric "\n"January to December returns." "See Raju, Rajan, Four and Five-Factor Models in the Indian Equities Market (March 10, 2022). Available at SSRN: https://ssrn.com/abstract=4054146 for details."\n\n  0 : Long Short Returns -- Monthly (235 rows x 6 cols)\n  1 : Annual Factors: January-December (19 rows x 6 cols)'
}
```

Explanation:
The `DESCR' dataframe shows the titles for the dataframes and their shape. In this case:

0 : Long Short Returns -- Monthly (235 rows x 6 cols)

1 : Annual Factors: January-December (19 rows x 6 cols)

Monthly Returns (0): Contains monthly returns for the long-short factors: MF, SMB, HML, WML, RF, and MKT. Indexed by Dates, with each row representing a monthly data point.

Annual Factors (1): Contains annual returns indexed by Years, with the same factors as above.

Description (DESCR):
A brief textual explanation of the dataset, including methodology references and links to relevant research, where appropriate, and the keys for other dataframes in the dictionary.
Note:
The keys 0 and 1 represent different datasets returned from the same query.
The structure may vary depending on the dataset queried.

### Usage Tips
Accessing DataFrames: Use keys 0 and 1 to access the specific DataFrames directly, for example, in this instance:

```python
monthly_returns = dataset[0]
annual_factors = dataset[1]
```

Viewing Metadata: Access the DESCR field to understand dataset structure and methodology.


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


### License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.



