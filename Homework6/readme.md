# Yfinance to Snowflake ETL DAG

This project is an **Apache Airflow DAG** that extracts stock price data from **Yahoo Finance** using the `yfinance` library and loads it into **Snowflake**. The DAG is designed to run daily, fetch data for a specified stock symbol, and store it in a Snowflake table.

## Project Structure

```plaintext
├── dags/
│   └── yfinance_to_snowflake_dag.py  # The main DAG code
└── README.md
```

## Requirements

- **Apache Airflow** with **Cloud Composer** or a self-hosted environment
- **Snowflake** account and connection details
- **Airflow Snowflake Provider**: `apache-airflow-providers-snowflake`
- **yfinance** library for data extraction

## DAG Overview

- **DAG Name**: `YfinanceToSnowflake`
- **Schedule**: Runs daily at 2:30 AM (`30 2 * * *`)
- **Tasks**:
  - `extract`: Extracts daily stock price data for a specific symbol from Yahoo Finance.
  - `load`: Loads the extracted data into a specified Snowflake table.

## Setup Instructions

1. **Install Airflow and Required Providers**:
   - Make sure `apache-airflow-providers-snowflake` is installed in your Cloud Composer environment or Airflow instance. This can be added to **PYPI Packages** in Cloud Composer.
   
2. **Configure Snowflake Connection in Airflow**:
   - Set up a connection in Airflow with the **Conn ID** `snowflake_conn` for Snowflake.
   - In the connection settings, enter your Snowflake account details, including account, username, password, warehouse, database, and schema.

3. **Airflow Variables** (Optional):
   - You can set `symbol` and `target_table` as Airflow variables for easy configuration.

4. **Create Target Table in Snowflake**:
   - The DAG will automatically create the target table if it does not exist. Make sure your Snowflake user has the necessary permissions.

## Code Explanation

### Functions

- **`get_next_day(date_str)`**:
  - Utility function to get the next day’s date in `"YYYY-MM-DD"` format.

- **`return_snowflake_conn()`**:
  - Establishes and returns a Snowflake connection using `SnowflakeHook`.

- **`get_logical_date()`**:
  - Retrieves the logical date from Airflow’s context for processing data by date.

- **`extract(symbol)`**:
  - Extracts stock data for the specified symbol from Yahoo Finance for the current logical date.
  - Converts the data to a dictionary for easier loading.

- **`load(d, symbol, target_table)`**:
  - Loads the extracted stock data into the specified Snowflake table.
  - Inserts data and handles any potential duplicates by deleting existing records for the same date.

### DAG Structure

1. **`extract` Task**:
   - Downloads daily stock data for the specified symbol.
   - Uses the logical date as the start date and the next day as the end date to retrieve a one-day range.

2. **`load` Task**:
   - Creates the target table in Snowflake if it doesn’t exist.
   - Deletes any existing records for the date to avoid duplicates.
   - Inserts the new data into Snowflake.

## Sample Code

### Define DAG in `yfinance_to_snowflake_dag.py`

```python
from airflow import DAG
from airflow.decorators import task
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
import yfinance as yf
from datetime import datetime, timedelta
...

with DAG(
    dag_id='YfinanceToSnowflake',
    start_date=datetime(2024, 10, 2),
    catchup=False,
    schedule_interval='30 2 * * *',
    tags=['ETL']
) as dag:
    target_table = "stock_db.raw_data.stock_prices"
    symbol = "AAPL"

    data = extract(symbol)
    load(data, symbol, target_table)
```

## Running the DAG

1. **Trigger DAG Manually** (Optional):
   - You can trigger the DAG manually from the Airflow UI to test it.

2. **Monitor and Troubleshoot**:
   - Airflow’s UI allows you to monitor task progress and troubleshoot any errors.
   - Logs for each task (`extract` and `load`) will provide insights into data retrieval and loading processes.

## Error Handling

- The `load` task has a `try-except` block to handle any issues with data insertion. If an error occurs, the transaction is rolled back to maintain data integrity.
- If the `extract` task retrieves no data, it raises an error to prevent an empty insert.

## Notes

- **Catchup**: Set to `False` to avoid backfilling missed runs.
- **Logical Date**: The DAG uses the Airflow `logical_date` to ensure consistency across task executions.

This ETL pipeline is modular and can be customized to handle additional symbols or tables by adjusting the `symbol` and `target_table` parameters.
