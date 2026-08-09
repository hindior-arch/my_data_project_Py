from pathlib import Path
from datetime import date

import pandas as pd
import streamlit as st



PROJECT_ROOT = Path(__file__).resolve().parent
FACT_FILE = PROJECT_ROOT / "data" / "gold" / "facttable.csv"

st.set_page_config(
    page_title="Summary Blog Morabehava",
    page_icon="📊",
    layout="wide",
)

st.markdown(
    """
    <style>
    span[data-baseweb="tag"] {
        background-color: #E2037E !important;
        color: white !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

@st.cache_data
def load_fact_table(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    df.columns = [column.strip().lower() for column in df.columns]
    return df


def find_column(
    df: pd.DataFrame,
    candidates: list[str],
    required: bool = True,
):
    for column in candidates:
        if column in df.columns:
            return column

    if required:
        raise KeyError(
            "Missing one of these columns: "
            f"{', '.join(candidates)}. "
            f"Available columns: {', '.join(df.columns)}"
        )

    return None


def to_number(df: pd.DataFrame, column: str | None) -> None:
    if column:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        ).fillna(0)


def format_money(value: float) -> str:
    return f"₪{value:,.2f}"


IMAGE_URL = (
    "https://i0.wp.com/morabehava.blog/wp-content/uploads/"
    "2019/08/cropped-%D7%A2%D7%93%D7%9B%D7%A0%D7%99-%D7%9C%D7%95%D7%92%D7%95.png"
    "?fit=733%2C665&ssl=1"
)

WEBSITE_URL = "https://morabehava.blog/"

title_col, image_col = st.columns([5, 1])

with title_col:
    st.title("Summary Blog Morabehava")
    st.caption("Dashboard source: Gold fact table")

with image_col:
    st.image(
        IMAGE_URL,
        width=100,
        link=WEBSITE_URL
    )

if not FACT_FILE.exists():
    st.error(f"Fact table was not found: {FACT_FILE}")
    st.info(
        "Update FACT_FILE at the top of app.py with the exact Gold CSV filename."
    )
    st.stop()

try:
    fact = load_fact_table(str(FACT_FILE))

    order_column = find_column(
        fact,
        ["order_id", "orderid"],
    )
    customer_column = find_column(
        fact,
        ["customer_id", "customerid"],
    )
    product_column = find_column(
        fact,
        ["product_name", "name", "item_name", "product"],
    )
    amount_column = find_column(
        fact,
        ["line_total", "amount", "sales_amount", "total"],
    )
    quantity_column = find_column(
        fact,
        ["quantity", "qty","sales_qty"],
        required=False,
    )
    date_column = find_column(
        fact,
        ["order_date", "date_created", "order_date_created"],
        required=False,
    )

except (KeyError, pd.errors.ParserError, UnicodeDecodeError) as error:
    st.error(str(error))
    st.stop()


to_number(fact, amount_column)
to_number(fact, quantity_column)

if date_column:
    fact[date_column] = pd.to_datetime(
        fact[date_column],
        errors="coerce",
        utc=True,
    )

valid_dates = (
    fact[date_column].dropna()
    if date_column
    else pd.Series(
        dtype="datetime64[ns, UTC]"
    )
)


if not valid_dates.empty:
    start_date = valid_dates.min().date()
    end_date = valid_dates.max().date()


    # פילטר טווח תאריכים
    selected_dates = st.sidebar.date_input(
        "Date range",
        value=(start_date, end_date),
        min_value=start_date,
        max_value=end_date,
    )


    # רשימת השנים שקיימות בנתונים
    available_years = sorted(
        valid_dates.dt.year.unique().tolist(),
        reverse=True,
    )


    current_year = date.today().year


    # ברירת מחדל: השנה הנוכחית.
    # אם היא לא קיימת, תיבחר השנה האחרונה בנתונים.
    default_years = (
        [current_year]
        if current_year in available_years
        else [available_years[0]]
    )


    selected_years = st.sidebar.multiselect(
        "Years",
        options=available_years,
        default=default_years,
    )


    month_names = {
        1: "January",
        2: "February",
        3: "March",
        4: "April",
        5: "May",
        6: "June",
        7: "July",
        8: "August",
        9: "September",
        10: "October",
        11: "November",
        12: "December",
    }


    month_numbers = list(month_names.keys())


    selected_months = st.sidebar.multiselect(
        "Months",
        options=month_numbers,
        default=month_numbers,
        format_func=lambda month_number: (
            month_names[month_number]
        ),
    )


    # מסנן טווח תאריכים
    if (
        isinstance(selected_dates, tuple)
        and len(selected_dates) == 2
    ):
        selected_start, selected_end = selected_dates

        date_mask = fact[date_column].dt.date.between(
            selected_start,
            selected_end,
        )

    elif (
        isinstance(selected_dates, tuple)
        and len(selected_dates) == 1
    ):
        selected_day = selected_dates[0]

        date_mask = (
            fact[date_column].dt.date == selected_day
        )

    else:
        date_mask = pd.Series(
            True,
            index=fact.index,
        )


    # מסנן שנים
    if selected_years:
        year_mask = fact[date_column].dt.year.isin(
            selected_years
        )
    else:
        year_mask = pd.Series(
            True,
            index=fact.index,
        )


    # מסנן חודשים
    if selected_months:
        month_mask = fact[date_column].dt.month.isin(
            selected_months
        )
    else:
        month_mask = pd.Series(
            True,
            index=fact.index,
        )


    # כל התנאים חייבים להתקיים
    filtered_fact = fact.loc[
        date_mask
        & year_mask
        & month_mask
    ].copy()


else:
    st.sidebar.info(
        "No valid date column was found. "
        "Date filters are disabled."
    )

    filtered_fact = fact.copy()


sales_amount = filtered_fact[amount_column].sum()
order_count = filtered_fact[order_column].nunique()

display_customers = filtered_fact[customer_column].replace(
    {0: pd.NA, "0": pd.NA, "": pd.NA}
)
unique_customers = display_customers.dropna().nunique()

total_quantity = (
    filtered_fact[quantity_column].sum()
    if quantity_column
    else 0
)

average_order = (
    sales_amount / order_count
    if order_count
    else 0
)


kpi_1, kpi_2, kpi_3, kpi_4, kpi_5 = st.columns(5)

kpi_1.metric("Total sales", format_money(sales_amount))
kpi_2.metric("Total quantity", f"{total_quantity:,.0f}")
kpi_3.metric("Unique customers", f"{unique_customers:,}")
kpi_4.metric("Orders", f"{order_count:,}")
kpi_5.metric("Average order", format_money(average_order))

st.divider()
st.subheader("Top 5 products")

if quantity_column:
    product_summary = (
        filtered_fact
        .groupby(product_column, as_index=False)
        .agg(
            quantity=(quantity_column, "sum"),
            sales=(amount_column, "sum"),
        )
    )
else:
    product_summary = (
        filtered_fact
        .groupby(product_column, as_index=False)
        .agg(
            quantity=(amount_column, "size"),
            sales=(amount_column, "sum"),
        )
    )


# חמשת המוצרים המובילים לפי כמות
quantity_summary = (
    product_summary
    .sort_values("quantity", ascending=False)
    .head(5)
)


# חמשת המוצרים המובילים לפי מכירות
sales_summary = (
    product_summary
    .sort_values("sales", ascending=False)
    .head(5)
)


PINK_COLOR = "#E2037E"


left, right = st.columns(2)


with left:
    st.write("Top products by quantity")

    quantity_chart = (
        quantity_summary
        .sort_values("quantity", ascending=False)
        .set_index(product_column)["quantity"]
    )

    st.bar_chart(
        quantity_chart,
        horizontal=True,
        sort=False,
        color=PINK_COLOR,
    )


with right:
    st.write("Top products by sales")

    sales_chart = (
        sales_summary
        .sort_values("sales", ascending=False)
        .set_index(product_column)["sales"]
    )

    st.bar_chart(
        sales_chart,
        horizontal=True,
        sort=False,
        color=PINK_COLOR,
    )


st.subheader("Top products table")
st.dataframe(
    product_summary,
    use_container_width=True,
    hide_index=True,
)

with st.expander("Data information"):
    st.write(f"Rows after filter: {len(filtered_fact):,}")
    st.write(f"Fact table: {FACT_FILE}")
    st.json(
        {
            "order": order_column,
            "customer": customer_column,
            "product": product_column,
            "amount": amount_column,
            "quantity": quantity_column,
            "date": date_column,
        }
    )


