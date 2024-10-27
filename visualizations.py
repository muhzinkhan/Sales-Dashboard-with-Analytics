import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io, base64
from collections import defaultdict
from typing import Tuple, Literal, Dict
from matplotlib.ticker import FuncFormatter
from matplotlib.figure import Figure


def encode_plt(ax) -> str:
    """encodes the axes/plt object for the flask app"""
    img = io.BytesIO()
    ax.savefig(img, format="png")
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    return plot_url


def top_n_products(
    products_table: pd.DataFrame, sales_table: pd.DataFrame, num: int = 10
) -> Tuple[pd.DataFrame, Figure, str]:
    """Top selling N products"""
    df = sales_table.merge(products_table, on="Product ID", how="left")[
        ["Product Name", "Total Sales"]
    ]

    top_n_products = (
        df.groupby("Product Name")
        .agg("sum")
        .sort_values(by="Total Sales", ascending=False)[:num]
    )

    # plot Top selling products
    plt.figure(figsize=(8, 5), dpi=140)

    colors = sns.color_palette("Blues", n_colors=num)[::-1]
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

    return top_n_products, plt, encode_plt(plt)


def yearly_sales_trend(
    sales_with_dates: pd.DataFrame,
) -> Tuple[pd.DataFrame, Figure, str]:
    """Yearly sales on a bar plot"""

    # Yearly Sales
    yearly_sales = sales_with_dates.pivot_table(
        index="Year", values="Total Sales", aggfunc="sum"
    )

    # No. of yticks
    y_axis_split = 3

    y_tickers = np.linspace(
        yearly_sales["Total Sales"].min(),
        yearly_sales["Total Sales"].max(),
        y_axis_split,
    )
    y_tick_labels = [f"$ {x/10**6:.2f} M" for x in (y_tickers)]

    # plot the figure
    plt.figure(figsize=(5, 4), dpi=130)

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
    # plt.title("Yearly Sales", pad=10, fontweight="bold")
    plt.tight_layout()

    return yearly_sales, plt, encode_plt(plt)


def qtr_sales_trend(sales_with_dates: pd.DataFrame) -> Tuple[pd.DataFrame, Figure, str]:
    """Qyarterly sales trend"""

    # Quarterly Sales
    qtrly_sales = sales_with_dates.pivot_table(
        index=["Year Qtr"], values="Total Sales", aggfunc="sum"
    )

    # No. of yticks
    y_axis_split = 6

    y_tickers = np.linspace(
        qtrly_sales["Total Sales"].min(),
        qtrly_sales["Total Sales"].max() + 1,
        y_axis_split,
    )
    y_tickers_labels = [f"$ {x/10**6:.2f} M" for x in y_tickers]

    plt.figure(figsize=(12, 6))

    sns.lineplot(x=qtrly_sales.index, y=qtrly_sales["Total Sales"])
    plt.xticks(rotation=45, font={"size": 12})
    plt.yticks(y_tickers, labels=y_tickers_labels, font={"size": 12})
    plt.grid(True, alpha=0.2)
    # plt.title("Sales Trend (Quarterly)", pad=10, fontweight="bold")
    plt.tight_layout()

    return qtrly_sales, plt, encode_plt(plt)


def monthly_sales_trend(
    sales_with_dates: pd.DataFrame,
) -> Tuple[pd.DataFrame, Figure, str]:
    """Monthly sales trend"""

    # Monthly Sales
    monthly_sales = sales_with_dates.pivot_table(
        index=["Year Monthname"], values="Total Sales", aggfunc="sum"
    )

    # No. of yticks
    y_axis_split = 4

    y_tickers = np.linspace(
        monthly_sales["Total Sales"].min(),
        monthly_sales["Total Sales"].max() + 1,
        y_axis_split,
    )
    y_tickers_labels = [f"$ {x/10**6:.2f} M" for x in y_tickers]

    plt.figure(figsize=(13, 6))

    plt.plot(monthly_sales.index, monthly_sales["Total Sales"])
    plt.xticks(rotation=45, font={"size": 11})
    plt.yticks(y_tickers, labels=y_tickers_labels, font={"size": 12})
    plt.grid(True, alpha=0.2)
    # plt.title("Sales Trend", pad=10, fontweight="bold")
    plt.tight_layout()

    return monthly_sales, plt, encode_plt(plt)


def daily_sales_trend(
    sales_with_dates: pd.DataFrame,
) -> Tuple[pd.DataFrame, Figure, str]:
    """Daily sales trend"""

    # Daily Sales
    daily_sales = sales_with_dates.pivot_table(
        index="Order Date", values="Total Sales", aggfunc="sum"
    )

    # Rolling window of 10
    window = 30

    plt.figure(figsize=(12, 6))
    sns.lineplot(
        x=daily_sales.index, y=daily_sales["Total Sales"].rolling(window=window).mean()
    )
    plt.xticks(rotation=45, fontsize=11)
    plt.yticks(fontsize=12)
    plt.grid(True, alpha=0.2)
    # plt.title(f"Daliy Sales Trend (Rolling window:{window})", pad=10, fontweight="bold")
    plt.tight_layout()

    return daily_sales, plt, encode_plt(plt)


def sales_trends(
    dates_table: pd.DataFrame,
    sales_table: pd.DataFrame,
    kind: Literal["yearly", "quarterly", "monthly", "daily"],
) -> Tuple[pd.DataFrame, Figure, str]:
    """Calls a function to plot the corresponding 'kind' of sales trend"""
    # Merge all dates with all sales
    df = dates_table.merge(
        sales_table,
        on="Order Date",
        how="left",
    )[list(dates_table.columns) + ["Total Sales"]]
    df.fillna(0, inplace=True)

    # Sales
    sales, plt, img = sales_plotters[kind.lower()](df)

    return sales, plt, img


def calculate_measures(
    sales_table: pd.DataFrame, products_table: pd.DataFrame, monthly_sales: pd.DataFrame
) -> Dict[str, str]:
    """Calculates all the measures required for the dashboard"""

    measure_data = {}

    total_sales = sales_table["Total Sales"].sum()
    total_sales_kpi = f"${total_sales:,}"
    measure_data["total_sales_kpi"] = total_sales_kpi

    monthly_avg_sales = monthly_sales["Total Sales"].mean().__round__(0)
    monthly_avg_sales_kpi = f"${monthly_avg_sales:,.0f}"
    measure_data["monthly_avg_sales_kpi"] = monthly_avg_sales_kpi

    sales_and_products = sales_table.merge(products_table, on="Product ID", how="left")

    sales_and_products["Total Cost"] = (
        sales_and_products["Cost"] * sales_and_products["Quantity"]
    )
    total_cost = sales_and_products["Total Cost"].sum()
    total_cost_kpi = f"${total_cost:,}"
    measure_data["total_cost_kpi"] = total_cost_kpi

    sales_and_products["Total Profit"] = (
        sales_and_products["Total Sales"] - sales_and_products["Total Cost"]
    )
    total_profit = sales_and_products["Total Profit"].sum()
    total_profit_kpi = f"${total_profit:,}"
    measure_data["total_profit_kpi"] = total_profit_kpi

    total_profit_margin = total_profit / total_sales * 100
    total_profit_margin_kpi = f"{total_profit_margin:.0f}%"
    measure_data["total_profit_margin_kpi"] = total_profit_margin_kpi

    return measure_data


def yearly_sales_dist_pie(
    yearly_sales: pd.DataFrame,
) -> Tuple[pd.DataFrame, Figure, str]:
    """Yearly sales ditribution on a pie chart"""
    palette_color = sns.color_palette("bright")
    explode = [
        2 / 10 if j == min(yearly_sales["Total Sales"]) else 0
        for i, j in zip(yearly_sales.index, yearly_sales["Total Sales"])
    ]

    # plotting data on pie chart
    plt.figure(figsize=(5, 7.45))
    plt.pie(
        yearly_sales["Total Sales"],
        labels=yearly_sales.index,
        colors=palette_color,
        autopct="%.0f%%",
        explode=explode,
        textprops={"fontsize": 15},
    )
    # plt.title("Yearly Sales Distribution", pad=10, fontweight="bold")
    plt.legend(loc="center", bbox_to_anchor=(0.5, -0.15), fontsize=15)
    plt.tight_layout()

    return yearly_sales, plt, encode_plt(plt)


def sales_heat_map(
    dates_table: pd.DataFrame, sales_table: pd.DataFrame
) -> Tuple[pd.DataFrame, Figure, str]:
    """Sales heat map"""

    # Merge all dates with all sales
    sales_with_dates = dates_table.merge(
        sales_table,
        on="Order Date",
        how="left",
    )[list(dates_table.columns) + ["Total Sales"]]
    sales_with_dates.fillna(0, inplace=True)

    sales_with_dates["Month Name"] = pd.Categorical(
        sales_with_dates["Month Name"],
        categories=[
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ],
        ordered=True,
    )

    heat_df = sales_with_dates.pivot_table(
        index="Month Name",
        columns="Year",
        values="Total Sales",
        aggfunc="sum",
        observed=True,
    )

    plt.figure(figsize=(6, 6))

    sns.heatmap(heat_df, annot=True, fmt=",.0f")
    # plt.title("Sales Heat Map", pad=10, fontweight="bold")
    plt.tight_layout()

    return heat_df, plt, encode_plt(plt)


# A dictionary for all the kinds of sales trend to be used in the 'sales_trends' method
sales_plotters = defaultdict(
    lambda: monthly_sales_trend,
    {
        "yearly": yearly_sales_trend,
        "quarterly": qtr_sales_trend,
        "monthly": monthly_sales_trend,
        "daily": monthly_sales_trend,
    },
)
