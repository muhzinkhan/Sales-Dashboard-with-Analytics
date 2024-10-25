# Optimize imports
from flask import Flask, render_template
import pandas as pd
from sqlalchemy import create_engine
from collections import defaultdict
from typing import DefaultDict
import re
import os
import dotenv
import io
import base64
from visualizations import top_selling_products, sales_trend


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

# Create Flask App
app = Flask(__name__)


def query_all(engine) -> DefaultDict[str, pd.DataFrame]:
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


# TODO unused
def query_one(engine, table_name) -> DefaultDict[str, pd.DataFrame]:
    """Queries all tables from the database"""
    dfs = defaultdict(pd.DataFrame)  # Defining a default dictionary for the dataframes
    query = f"SELECT * FROM `{table_name}`;"
    df = pd.read_sql(query, con=engine)
    return df


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


def encode_plt(plt) -> str:
    """encodes the axes(plt) object for the flask app"""
    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    return plot_url


def generate_dates_table(date_min, date_max, sales_table) -> pd.DataFrame:
    date_min = sales_table['Order Date'].min()
    date_max = sales_table['Order Date'].max()
    date_min, date_max

    calender_dates = pd.date_range(start=date_min, end=date_max, freq='D')
    dates_table = pd.DataFrame(calender_dates, columns=['Order Date'])
    dates_table



# <------------------ Main Script ------------------>
# dfs = query_all(engine=engine)
# sales_table = concatinate_all_sales_table(dfs=dfs)


# KPI's -------------->


## Sales Trend
# yearly_sales, plt = sales_trend(sales_table)
# plt.show()

## Total Sales

## Total Cost

## Total Profit

## Yearly Sales Distribution

## Sales Heat Map


@app.route("/")
def dashboard():
    # Read data from SQL
    dfs = query_all(engine=engine)
    sales_table = concatinate_all_sales_table(dfs=dfs)

    # Create a plot for the top 10 selling products
    top_10_products_table, top_10_products_table_plt = top_selling_products(
        products_table=dfs["products"], sales_table=sales_table, rank=10
    )




    return render_template(
        "index.html",
        total_sales="NA;;;;",
        top_selling_product="NA",
        plot_url=encode_plt(top_10_products_table_plt),
    )


if __name__ == "__main__":
    app.run(debug=True)
