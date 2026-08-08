import pandas as pd
from pathlib import Path
from datetime import datetime

# נתיבים
folder_path_raw_line_items = Path("D:/Project/Naya/Py_env/data/raw/line_items")
folder_path_raw_customers = Path("D:/Project/Naya/Py_env/data/raw/customers")
folder_path_raw_products = Path("D:/Project/Naya/Py_env/data/raw/products")
folder_path_gold = Path("D:/Project/Naya/Py_env/data/gold")


file_pathorderslineraw = folder_path_raw_line_items / "line_items_raw.csv"
file_pathcustomersraw = folder_path_raw_customers / "customers_raw.csv"
file_pathproductsraw = folder_path_raw_products / "products_raw.csv"
file_pathorderslinegold = folder_path_gold / "facttable.csv"


dforderslineraw = pd.read_csv(file_pathorderslineraw)
dfcustomersraw = pd.read_csv(file_pathcustomersraw)
dfproductsraw = pd.read_csv(file_pathproductsraw)
dffacttableraw = pd.read_csv(file_pathorderslinegold)


# המרת עמודות המכירה למספרים
dforderslineraw["total"] = pd.to_numeric(
    dforderslineraw["total"],
    errors="coerce"
)

dffacttableraw["sales_amount"] = pd.to_numeric(
    dffacttableraw["sales_amount"],
    errors="coerce"
)


# בדיקת סכום מכירות
sum_sales_raw = dforderslineraw["total"].sum()
sum_sales_gold = dffacttableraw["sales_amount"].sum()
difference_sales = sum_sales_gold - sum_sales_raw


# בדיקת כמות לקוחות ייחודיים
count_customers_raw = dfcustomersraw["id"].nunique()
count_customers_gold = dffacttableraw["customer_id"].nunique()
difference_customers = (
    count_customers_gold - count_customers_raw
)


# בדיקת כמות מוצרים ייחודיים
count_products_raw = dfproductsraw["id"].nunique()
count_products_gold = dffacttableraw["product_id"].nunique()
difference_products = (
    count_products_gold - count_products_raw
)


# זמן ביצוע הבדיקות
check_time = datetime.now().strftime(
    "%Y-%m-%d %H:%M:%S"
)


# יצירת טבלת תוצאות
checks = pd.DataFrame([
    {
        "check_time": check_time,
        "metric": "sales_amount_sum",
        "raw_value": sum_sales_raw,
        "gold_value": sum_sales_gold,
        "difference": difference_sales,
        "passed": difference_sales == 0
    },
    {
        "check_time": check_time,
        "metric": "unique_customers_count",
        "raw_value": count_customers_raw,
        "gold_value": count_customers_gold,
        "difference": difference_customers,
        "passed": difference_customers == 0
    },
    {
        "check_time": check_time,
        "metric": "unique_products_count",
        "raw_value": count_products_raw,
        "gold_value": count_products_gold,
        "difference": difference_products,
        "passed": difference_products == 0
    }
])


# הדפסה למסך
print("\n" + "=" * 80)
print("Gold Validation Checks")
print("=" * 80)

print(checks.to_string(index=False))


# יצירת תיקיית logs
project_dir = folder_path_gold.parent.parent
log_dir = project_dir / "logs"
log_dir.mkdir(parents=True, exist_ok=True)


# נתיב לוג מצטבר
gold_log_path = log_dir / "gold_log.csv"


# הוספת תוצאות ללוג המצטבר
checks.to_csv(
    gold_log_path,
    mode="a",
    header=not gold_log_path.exists(),
    index=False,
    encoding="utf-8-sig"
)


# פלט סופי
print("\n" + "=" * 80)
print("Gold validation log saved")
print("=" * 80)
print(f"Log path: {gold_log_path.resolve()}")
print(f"Log exists: {gold_log_path.exists()}")