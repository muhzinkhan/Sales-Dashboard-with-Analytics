import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import DefaultDict
from matplotlib.ticker import FuncFormatter


def top_selling_products(
    products_table: pd.DataFrame, sales_table: pd.DataFrame, rank: int
) -> pd.DataFrame:
    """Top selling products"""
    df = sales_table.merge(products_table, on="Product ID", how="left")[
        ["Product Name", "Total Sales"]
    ]

    top_n_products = (
        df.groupby("Product Name")
        .agg("sum")
        .sort_values(by="Total Sales", ascending=False)[:rank]
    )

    # plot Top selling products
    plt.figure(figsize=(8, 5))

    colors = sns.color_palette("Blues", n_colors=rank)[::-1]
    ax = sns.barplot(
        data=top_n_products,
        x="Total Sales",
        y=top_n_products.index,
        hue=top_n_products.index,
        palette=colors,
        orient="h",
    )
    ax.margins(x=0.22, y=0)

    for index, value in enumerate(top_n_products["Total Sales"]):
        ax.text(value + 10000, index, f"{value:,} $", ha="left")

    formatter = FuncFormatter(lambda x, _: f"{x//1000:.0f}K")
    ax.xaxis.set_major_formatter(formatter)
    ax.set_xlabel("Total Sales ($)", labelpad=10)
    ax.set_ylabel("Product Name", labelpad=10)
    plt.grid(True, axis="x", alpha=0.3)
    # plt.title(f"Top {rank} Products", pad=10, fontweight="bold")
    plt.tight_layout()

    return top_n_products, plt


def sales_trend(sales_table):
    """Plot Sales trend year-wise"""
    df3 = sales_table[["Order Date", "Total Sales"]]
    df3

    # create dates table
    # TODO make this a different function
    date_min = sales_table["Order Date"].min()
    date_max = sales_table["Order Date"].max()
    date_min, date_max

    calender_dates = pd.date_range(start=date_min, end=date_max, freq="D")
    dates_table = pd.DataFrame(calender_dates, columns=["Order Date"])
    dates_table

    # Merge all dates with all sales
    df4 = dates_table.merge(
        sales_table,
        on="Order Date",
        how="left",
    )[["Order Date", "Total Sales"]]
    df4.fillna(0, inplace=True)
    df4

    df4["Year"] = df4["Order Date"].dt.year
    df4["Qtr"] = df4["Order Date"].dt.quarter
    df4["Month Name"] = df4["Order Date"].dt.month_name()

    df4["Year Qtr"] = df4["Year"].astype(str) + " Qtr " + df4["Qtr"].astype(str)
    df4["Year Monthname"] = df4["Order Date"].dt.strftime("%Y %B")
    df4

    # Yearly sales
    yearly_sales = df4.pivot_table(index="Year", values="Total Sales", aggfunc="sum")
    yearly_sales.map(lambda x: f"{x:,}")

    y_axis_split = 3

    y_tickers = np.linspace(
        yearly_sales["Total Sales"].min(),
        yearly_sales["Total Sales"].max(),
        y_axis_split,
    )
    y_tick_labels = [f"$ {x/10**6:.2f} M" for x in (y_tickers)]

    ax = sns.barplot(x=yearly_sales.index, y=yearly_sales["Total Sales"])
    plt.yticks(y_tickers, labels=y_tick_labels)
    plt.xlabel("")
    ax.margins(x=0.05, y=0.1)

    for p in ax.patches:
        ax.annotate(
            f"$ {p.get_height():,.0f}",
            xy=(p.get_x() + p.get_width() / 2.0, p.get_height()),
            ha="center",
            va="center",
            xytext=(0, 9),
            textcoords="offset points",
        )
    plt.title("Yearly Sales", pad=10, fontweight="bold")
    plt.tight_layout()

    return yearly_sales, plt
