import pandas as pd
from sqlalchemy import create_engine
from collections import defaultdict
from typing import DefaultDict
import re
import os
import dotenv


# load Environmental variables
dotenv.load_dotenv()

DATABASE_NAME = os.getenv("DATABASE_NAME")
HOST = os.getenv("HOST")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")


# Create MySQL connection
engine = create_engine(
    f"mysql+mysqlconnector://{USERNAME}:{PASSWORD}@{HOST}/{DATABASE_NAME}"
)


def fetch_all(engine) -> DefaultDict[str, pd.DataFrame]:
    """Queries all tables from the database"""

    dfs = defaultdict(pd.DataFrame)  # Defining a default dictionary for the dataframes
    tables_query = "SHOW Tables"
    tables = pd.read_sql(tables_query, con=engine)

    for table_name in tables.iloc[:, 0].values:
        query = f"SELECT * FROM `{table_name}`;"
        dfs[table_name] = pd.read_sql(query, con=engine)
        # TODO delete this print statement
        # print(f"<------------------{table_name} ------------------>\n\n", dfs[table_name].head(), '\n\n')

    return dfs


def concatinate_all_sales_table(dfs: DefaultDict[str, pd.DataFrame]) -> pd.DataFrame:
    """Combines all sales table in the dictionary of tables into one dataframe and calculates the total sales"""

    all_sales_tables = defaultdict(pd.DataFrame)

    for table_name, df in dfs.items():
        if re.search(r"\d+", table_name) and re.search(
            r"\bsales\b", table_name, re.IGNORECASE
        ):
            all_sales_tables[table_name] = df

    concat_sales_table = pd.concat(all_sales_tables.values(), ignore_index=True)

    # Create a new column called 'Total Sales'
    concat_sales_table["Total Sales"] = (
        concat_sales_table["Quantity"] * concat_sales_table["Price"]
    )

    return concat_sales_table


# <------------------ Main Script ------------------>
dfs = fetch_all(engine=engine)
sales_table = concatinate_all_sales_table(dfs=dfs)
print(sales_table)
