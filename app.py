from flask import Flask, render_template, request, send_file, redirect, url_for
import pandas as pd
from sqlalchemy import create_engine
from collections import defaultdict
from typing import DefaultDict
import re, os, base64, dotenv
import visualizations as vis


# load Environmental variables
dotenv.load_dotenv()

DIALECT = "mysql"
DRIVER = "mysqlconnector"
DATABASE_NAME = os.getenv("DATABASE_NAME")
HOST = os.getenv("HOST")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")


# Create MySQL connection
engine = create_engine(
    f"{DIALECT}+{DRIVER}://{USERNAME}:{PASSWORD}@{HOST}/{DATABASE_NAME}"
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


def generate_dates_table(sales_table: pd.DataFrame) -> pd.DataFrame:
    """Generate dates with necessary measures"""
    date_min = sales_table["Order Date"].min()
    date_max = sales_table["Order Date"].max()

    calender_dates = pd.date_range(start=date_min, end=date_max, freq="D")
    dates_table = pd.DataFrame(calender_dates, columns=["Order Date"])

    dates_table["Year"] = dates_table["Order Date"].dt.year
    dates_table["Qtr"] = dates_table["Order Date"].dt.quarter
    dates_table["Month Name"] = dates_table["Order Date"].dt.month_name()

    dates_table["Year Qtr"] = (
        dates_table["Year"].astype(str) + " Qtr " + dates_table["Qtr"].astype(str)
    )
    dates_table["Year Monthname"] = dates_table["Order Date"].dt.strftime("%Y %B")

    return dates_table


@app.route("/")
def dashboard():

    # Read data from SQL Database
    dfs = query_all(engine=engine)
    table_names = dfs.keys()
    sales_table = concatinate_all_sales_table(dfs=dfs)
    dates_table = generate_dates_table(sales_table=sales_table)

    # dictionary for all measures for rendering in html
    measure_data = defaultdict(str)

    # dictionary for all visualizations for rendering in html
    plot_data = defaultdict(tuple)

    # Create a plot for the top 10 selling products
    top_products_num = 10
    plot_data["top_n_products"] = vis.top_n_products(
        products_table=dfs["products"], sales_table=sales_table, num=top_products_num
    )

    # Create a plot for yearly sales trend
    plot_data["yearly_sales_trend"] = vis.sales_trends(
        dates_table, sales_table, kind="yearly"
    )

    # Create a plot for quarterly sales trend
    plot_data["quarterly_sales_trend"] = vis.sales_trends(
        dates_table, sales_table, kind="quarterly"
    )

    # Create a plot for monthly sales trend
    plot_data["monthly_sales_trend"] = vis.sales_trends(
        dates_table, sales_table, kind="monthly"
    )

    # Calculates all the measures for the dashboard
    measure_data = vis.calculate_measures(
        sales_table=sales_table,
        products_table=dfs["products"],
        monthly_sales=plot_data["monthly_sales_trend"][0],
    )

    # Create a pie chart for yearly sales proportion
    plot_data["yearly_sales_distribution"] = vis.yearly_sales_dist_pie(
        plot_data["yearly_sales_trend"][0]
    )

    # Create a heatmap for all the sales that  happened
    plot_data["sales_heat_map"] = vis.sales_heat_map(
        dates_table=dates_table, sales_table=sales_table
    )

    return render_template(
        "index.html",
        measure_data=measure_data,
        plot_data=plot_data,
        table_names=table_names,
        top_products_num=top_products_num,
    )


@app.route("/download", methods=["POST"])
def download():
    plot_data = request.form.get("data")

    # Decode the base64 string
    image_data = base64.b64decode(plot_data)

    # Create an output file and write the image data
    with open(f"static/img/session/downloaded_plot.png", "wb") as file:
        file.write(image_data)

    return send_file(
        f"static/img/session/downloaded_plot.png",
        as_attachment=True,
        download_name=f"downloaded_plot.png",
    )


@app.route("/tables")
def tables():
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run(debug=True)
