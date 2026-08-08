import os
import pandas as pd
from datetime import datetime


# ============================================================
# הגדרות נתיבים
# ============================================================

PROJECT_ROOT = r"D:\Project\Naya\Py_env"

raw_folder = os.path.join(
    PROJECT_ROOT,
    "data",
    "raw"
)

curated_folder = os.path.join(
    PROJECT_ROOT,
    "data",
    "curated"
)

log_folder = os.path.join(
    PROJECT_ROOT,
    "logs"
)

os.makedirs(curated_folder, exist_ok=True)
os.makedirs(log_folder, exist_ok=True)


# קובץ לוג מצטבר
audit_log_path = os.path.join(
    log_folder,
    "raw_to_curated_log.csv"
)


# ============================================================
# פונקציות עזר
# ============================================================

def append_audit_log(rows):
    """
    מוסיף רשומות חדשות לקובץ לוג מצטבר.
    """

    audit_df = pd.DataFrame(rows)

    file_exists = os.path.exists(audit_log_path)

    audit_df.to_csv(
        audit_log_path,
        mode="a",
        index=False,
        header=not file_exists,
        encoding="utf-8-sig"
    )


def load_raw_file(
    entity_folder: str,
    file_name: str
) -> pd.DataFrame:
    """
    קורא קובץ מתוך:
    data/raw/<entity_folder>/<file_name>
    """

    file_path = os.path.join(
        raw_folder,
        entity_folder,
        file_name
    )

    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"RAW file not found: {file_path}"
        )

    print(f"Loading RAW file: {file_path}")

    df = pd.read_csv(file_path)

    return df


def check_required_columns(
    df: pd.DataFrame,
    required_columns: list,
    entity_name: str
):
    """
    בודק שכל העמודות הנדרשות קיימות.
    """

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise KeyError(
            f"Missing columns in {entity_name}: "
            f"{missing_columns}"
        )


def save_curated_file(
    df: pd.DataFrame,
    entity_name: str,
    file_name: str,
    source_file: str,
    run_timestamp: str
):
    """
    שומר DataFrame בתיקיית:
    data/curated/<entity_name>
    """

    entity_folder = os.path.join(
        curated_folder,
        entity_name
    )

    os.makedirs(
        entity_folder,
        exist_ok=True
    )

    target_file = os.path.join(
        entity_folder,
        file_name
    )

    df.to_csv(
        target_file,
        index=False,
        encoding="utf-8-sig"
    )

    audit_row = {
        "run_timestamp": run_timestamp,
        "entity_name": entity_name,
        "action": "saved_to_curated",
        "source_file": source_file,
        "target_file": target_file,
        "rows": len(df),
        "columns": len(df.columns),
        "file_exists": os.path.exists(target_file),
        "file_size_bytes": os.path.getsize(target_file)
    }

    print(
        f"Saved CURATED | {entity_name} -> {target_file}"
    )

    return audit_row


# ============================================================
# Orders
# ============================================================

def process_orders():
    source_file = os.path.join(
        raw_folder,
        "orders",
        "orders_raw.csv"
    )

    df = load_raw_file(
        "orders",
        "orders_raw.csv"
    )

    df.columns = df.columns.str.lower()

    df = df.rename(
        columns={
            "id": "order_id"
        }
    )

    required_columns = [
        "order_id",
        "payment_method_title"
    ]

    check_required_columns(
        df,
        required_columns,
        "orders"
    )

    df = df[required_columns]

    return df, source_file


# ============================================================
# Products
# ============================================================

def process_products():
    source_file = os.path.join(
        raw_folder,
        "products",
        "products_raw.csv"
    )

    df = load_raw_file(
        "products",
        "products_raw.csv"
    )

    df.columns = df.columns.str.lower()

    df = df.rename(
        columns={
            "id": "product_id",
            "name": "product_name",
            "status": "product_status",
            "price": "product_price",
            "date_created": "product_date_created",
            "date_modified": "product_date_modified"
        }
    )

    required_columns = [
        "product_id",
        "product_name",
        "product_status",
        "product_price",
        "product_date_created",
        "product_date_modified"
    ]

    check_required_columns(
        df,
        required_columns,
        "products"
    )

    df = df[required_columns]

    return df, source_file


# ============================================================
# Customers
# ============================================================

def process_customers():
    source_file = os.path.join(
        raw_folder,
        "customers",
        "customers_raw.csv"
    )

    df = load_raw_file(
        "customers",
        "customers_raw.csv"
    )

    df.columns = df.columns.str.lower()

    df = df.rename(
        columns={
            "id": "customer_id",
            "date_created": "customer_date_created",
            "date_modified": "customer_date_modified"
        }
    )

    required_columns = [
        "customer_id",
        "email",
        "billing_city",
        "customer_date_created",
        "customer_date_modified"
    ]

    check_required_columns(
        df,
        required_columns,
        "customers"
    )

    df = df[required_columns]

    return df, source_file


# ============================================================
# Line Items
# ============================================================

def process_line_items():
    source_file = os.path.join(
        raw_folder,
        "line_items",
        "line_items_raw.csv"
    )

    df = load_raw_file(
        "line_items",
        "line_items_raw.csv"
    )

    df.columns = df.columns.str.lower()

    df = df.rename(
        columns={
            "quantity": "sales_qty",
            "total": "sales_amount"
        }
    )

    required_columns = [
        "order_id",
        "order_date_created",
        "order_date_modified",
        "customer_id",
        "order_status",
        "product_id",
        "sales_qty",
        "sales_amount"
    ]

    check_required_columns(
        df,
        required_columns,
        "line_items"
    )

    df = df[required_columns]

    return df, source_file


# ============================================================
# הרצת RAW → CURATED
# ============================================================

def run_raw_to_curated():
    print("=" * 80)
    print("RAW TO CURATED PROCESSING STARTED")
    print("=" * 80)

    run_timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    audit_rows = []

    # --------------------------------------------------------
    # Orders
    # --------------------------------------------------------

    orders_df, orders_source = process_orders()

    orders_audit = save_curated_file(
        df=orders_df,
        entity_name="orders",
        file_name="orders_latest.csv",
        source_file=orders_source,
        run_timestamp=run_timestamp
    )

    audit_rows.append(orders_audit)

    # --------------------------------------------------------
    # Products
    # --------------------------------------------------------

    products_df, products_source = process_products()

    products_audit = save_curated_file(
        df=products_df,
        entity_name="products",
        file_name="products_latest.csv",
        source_file=products_source,
        run_timestamp=run_timestamp
    )

    audit_rows.append(products_audit)

    # --------------------------------------------------------
    # Customers
    # --------------------------------------------------------

    customers_df, customers_source = process_customers()

    customers_audit = save_curated_file(
        df=customers_df,
        entity_name="customers",
        file_name="customers_latest.csv",
        source_file=customers_source,
        run_timestamp=run_timestamp
    )

    audit_rows.append(customers_audit)

    # --------------------------------------------------------
    # Line Items
    # --------------------------------------------------------

    line_items_df, line_items_source = process_line_items()

    line_items_audit = save_curated_file(
        df=line_items_df,
        entity_name="line_items",
        file_name="line_items_latest.csv",
        source_file=line_items_source,
        run_timestamp=run_timestamp
    )

    audit_rows.append(line_items_audit)

    # --------------------------------------------------------
    # שמירת Audit Log
    # --------------------------------------------------------

    append_audit_log(audit_rows)

    print()
    print(
        f"Audit log appended to: {audit_log_path}"
    )

    print("=" * 80)
    print("RAW TO CURATED PROCESSING FINISHED")
    print("=" * 80)

    return (
        orders_df,
        products_df,
        customers_df,
        line_items_df
    )


# ============================================================
# נקודת כניסה
# ============================================================

if __name__ == "__main__":
    run_raw_to_curated()