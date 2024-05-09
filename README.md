# IndiaFactorLibrary

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Introduction](#introduction)
- [Key Features](#key-features)
- [Installation](#installation)
- [Requirements](#requirements)
- [Usage](#usage)
- [Available Datasets](#available-datasets)
  - [Accessing Datasets](#accessing-datasets)
  - [Example of a Use Case](#example-of-a-use-case)
  - [Usage Tips](#usage-tips)
- [Documentation](#documentation)
  - [IndiaFactorLibrary Class (Invespar Data Library: Fama-French Factors, Momentum, and Low-Risk Factors for the Indian Market)](#indiafactorlibrary-class-invespar-data-library-fama-french-factors-momentum-and-low-risk-factors-for-the-indian-market)
  - [License](#license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


## Introduction

The **IndiaFactorLibrary** is a python package for remote data access for Invespar's Data Library: Fama-French Factors, Momentum, and Low-Risk Factors for the Indian Market.

## Key Features

For practitioners, students, researchers, and other finance professionals seeking to explore factor investing within the Indian equities market, IndiaFactorLibrary fills a crucial gap. It provides convenient access to a comprehensive collection of Indian equity factors, similar to the functionality offered by pandas-datareader for the Ken French Data Library. Explore the available factors at [Invespar's Data Library: Fama-French Factors, Momentum, and Low-Risk Factors for the Indian Market](http://invespar.com/research).

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

**Fama French Factors Plus Momentum Factor**

| Symbol                | Description                                           |
|-----------------------|-------------------------------------------------------|
| **ff4**               | Fama-French 4 factors                                 |
| **ff6**               | Fama-French 6 factors                                 |


**6 Portfolios: 2x3 sorts on Size and Target Characteristics**
| Symbol                | Description                                           |
|-----------------------|-------------------------------------------------------|
| **size_value_portfolios** | 6 portfolios sorted by size and value (2x3)       |
| **size_op_portfolios** | 6 portfolios sorted by size and operating profitability (2x3) |
| **size_inv_portfolios** | 6 portfolios sorted by size and investment (2x3)    |
| **size_mom_portfolios** | 6 portfolios sorted by size and momentum (2x3)      |

**10 Portfolios: Decile univariate sorts**
| Symbol                | Description                                           |
|-----------------------|-------------------------------------------------------|
| **size_deciles**      | 10 portfolios sorted by size                          |
| **btm_deciles**       | 10 portfolios sorted by book-to-market ratio          |
| **op_deciles**        | 10 portfolios sorted by operating profitability       |
| **in_deciles**        | 10 portfolios sorted by investment                    |
| **mom_deciles**       | 10 portfolios sorted by momentum                      |
| **vol_deciles**       | 10 portfolios sorted by volatility                    |

**25 Portfolios: 5x5 sorts on Size and Target Characteristics**
| Symbol                | Description                                           |
|-----------------------|-------------------------------------------------------|
| **size_btm_5x5**      | 5x5 portfolios sorted by size and book-to-market ratio |
| **size_op_5x5**       | 5x5 portfolios sorted by size and operating profitability |
| **size_inv_5x5**      | 5x5 portfolios sorted by size and investment          |
| **size_mom_5x5**      | 5x5 portfolios sorted by size and momentum            |
| **size_vol_5x5**      | 5x5 portfolios sorted by size and volatility          |

**Low-Risk Factors and Sub-Portfolios**
| Symbol                | Description                                           |
|-----------------------|-------------------------------------------------------|
| **low_risk_factors**  | Low-risk factors                                      |
| **low_risk_factors_vol** | Low-risk factors based on realized volatility      |
| **low_risk_factors_bab_fp** | Betting Against Beta (Frazzini-Pedersen methodology) |
| **low_risk_factors_bab_ff** | Ex-ante BAB methodology (Fama-French 2x3 construction) |
| **low_risk_factors_bab_capm** | BAB using CAPM Beta (FF 2x3 construction)     |
| **low_risk_factors_ivol** | Low-risk factors using idiosyncratic volatility   |

**52-week High Effect**
| Symbol                | Description                                           |
|-----------------------|-------------------------------------------------------|
| **f2_week_high**      | 52-week high effect                                   |

**Conservative Formula**
| Symbol                | Description                                           |
|-----------------------|-------------------------------------------------------|
| **cms_portfolios**    | CMS (Conservative Formula) portfolios                 |

**Breakpoints**
| Symbol                | Description                                           |
|-----------------------|-------------------------------------------------------|
| **ff5_breakpoints**   | Breakpoints for Fama-French 5 factors                 |
| **mom_breakpoints**   | Breakpoints for momentum factors                      |
| **lovol_breakpoints** | Breakpoints for low-volatility factors                |

Note:
This list is updated from Invespar's website as of April 2024. The datasets available may change over time as new data is added or removed. For further details on detailed references, please refer to the papers available at https://papers.ssrn.com/sol3/cf_dev/AbsByAuth.cfm?per_id=3354364.

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

The `read` method retrieves a dataset and returns it as a dictionary of DataFrames. The output includes several elements: 

* **DataFrames**: The dictionary contains one or more DataFrames, each accessible by a numerical key (e.g., 0, 1).
* **Descriptions** (`DESCR`): The `DESCR` key provides a textual explanation of the dataset, including information about the methodology and references to relevant research. It also indicates the structure of the returned DataFrames.


Here's an example of the output structure:

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

In this example:

* **DataFrame 0 (Long Short Returns -- Monthly (235 rows x 6 cols)):** contains monthly returns for the market factor (MF) and long-short factors size (SMB), value (HML), and momentum (WML). In addition, it has risk-free rate (RF) and market return (MKT). Long-short factors represent hypothetical strategies that involve taking long positions in stocks with specific characteristics while simultaneously taking short positions in stocks with opposite characteristics. Examples of these characteristics include:

  * **Size (SMB):** Long positions in small-size stocks and short positions in big-size stocks.
  * **Value (HML):** Long positions in value stocks (high book-to-market ratio) and short positions in expensive stocks (low book-to-market ratio).
  * **Profitability (RMW):** Long positions in stocks with robust operating profitability and short positions in stocks with weak operating profitability.
  * **Investment (CMA):** Long positions in stocks with conservative investment and short positions in stocks with aggressive investment.
  * **Momentum (WML):** Long positions in stocks with high past returns and short positions in stocks with low past returns.
  * **Other "factors":** The library also includes factors based on volatility/low-risk, the 52-week high effect, and the Conservative Formula.

Analysing these factors helps understand the drivers of market returns beyond overall market movements. For a detailed analysis of Fama-French factors and their application in the Indian equities market, refer to Raju, Rajan (2022), "*Four and Five-Factor Models in the Indian Equities Market*", available at https://papers.ssrn.com/abstract_id=4054146.

* **DataFrame 1 (Annual Factors: January-December (19 rows x 6 cols)):** contains annual returns for the same factors.
* **DataFrame `DESCR`:** provides additional information about the dataset and its structure. It also includes methodology references and links to relevant research, where appropriate, and the keys for other dataframes in the dictionary.

Keep in mind that the exact structure and content of the output may vary depending on the specific dataset you retrieve. Always read the `DESCR` first.

### Example of a Use Case 

Here's a code snippet demonstrating a simple use case of `IndiaFactorLibrary`:

```python
from indiafactorlibrary import IndiaFactorLibrary
import matplotlib.pyplot as plt

# Initialize the library
ifl = IndiaFactorLibrary()

# Read the Fama-French 4 factors and size decile portfolios
ff4_data = ifl.read('ff4')
size_deciles = ifl.read('size_deciles')

# Access the Value Weighted monthly returns DataFrames
ff4_monthly_returns = ff4_data[0]
size_deciles_monthly_returns = size_deciles[0]

# Calculate the cumulative returns for SMB and the smallest size decile
smb_cumulative_returns = (1 + ff4_monthly_returns['SMB']/100).cumprod()
smallest_decile_cumulative_returns = (1 + size_deciles_monthly_returns['Lo Decile']/100).cumprod()

# Plot the cumulative returns
plt.plot(smb_cumulative_returns, label="SMB")
plt.plot(smallest_decile_cumulative_returns, label="Smallest Size Decile")
plt.xlabel("Date")
plt.ylabel("Cumulative Returns")
plt.title("SMB vs. Smallest Size Decile Performance")
plt.legend()
plt.show()
```

**Explanation:**

* **Import Libraries:** Imports IndiaFactorLibrary and matplotlib for plotting.
* **Read Data:** Retrieves Fama-French 4 factors and size decile portfolios.
* **Access DataFrames:** Select the DataFrames containing monthly returns.
* **Calculate Cumulative Returns:** Calculates the cumulative returns for the SMB factor and the smallest size decile portfolio. **The data is in percent; we convert it to decimal**.
* **Plot Returns:** Plots the cumulative returns over time, allowing for visual comparison.

This example demonstrates how to retrieve data using IndiaFactorLibrary and perform a simple analysis, showcasing the library's functionality and potential applications.

### Usage Tips

Accessing DataFrames: Use keys like 0 and 1 to access the specific DataFrames directly, for example, in this instance:

```python
monthly_returns = dataset[0]
annual_factors = dataset[1]
```

Viewing Metadata: Access the `DESCR` field to understand dataset structure and methodology.


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

**Properties:**

- **url:**  
  API URL for data access.


### License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.



