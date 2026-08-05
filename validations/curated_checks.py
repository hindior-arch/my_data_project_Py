import os
import pandas as pd
from datetime import datetime


PROJECT_ROOT = r"D:\Project\Naya\Py_env"

curated_folder = os.path.join(PROJECT_ROOT, "data", "curated")
gold_folder = os.path.join(PROJECT_ROOT, "data", "gold")
log_folder = os.path.join(PROJECT_ROOT, "logs")
os.makedirs(gold_folder, exist_ok=True)
os.makedirs(log_folder, exist_ok=True)

audit_log_path = os.path.join(log_folder, "curated_raw_log.csv")


def append_audit_log(rows):
    audit_df = pd.DataFrame(rows)
    file_exists = os.path.exists(audit_log_path)
    audit_df.to_csv(
        audit_log_path,
        mode="a",
        index=False,
        header=not file_exists,
        encoding="utf-8-sig"
    )


def load_latest_file(entity_folder: str, file_name: str) -> pd.DataFrame:
    file_path = os.path.join(curated_folder, entity_folder, file_name)
    df = pd.read_csv(file_path)
    return df


def process_orders():
    df = load_latest_file("orders", "orders_latest.csv")
    df.columns = df.columns.str.lower()

    df = df.rename(columns={"id": "order_id"})
    df = df[["order_id", "payment_method_title"]]
    return df


def process_products():
    df = load_latest_file("products", "products_latest.csv")
    df.columns = df.columns.str.lower()

    df = df.rename(columns={
        "id": "product_id",
        "name": "product_name",
        "status": "product_status",
        "price": "product_price",
        "date_created": "product_date_created",
        "date_modified": "product_date_modifed"
    })

    df = df[[
        "product_id",
        "product_name",
        "product_status",
        "product_price",
        "product_date_created",
        "product_date_modifed"
    ]]
    return df


def process_customers():
    df = load_latest_file("customers", "customers_latest.csv")
    df.columns = df.columns.str.lower()

    df = df.rename(columns={
        "id": "customer_id",
        "date_created": "customer_date_created",
        "date_modified": "customer_date_modifed"
    })

    df = df[[
        "customer_id",
        "email",
        "billing_city",
        "customer_date_created",
        "customer_date_modifed"
    ]]
    return df


def process_line_items():
    df = load_latest_file("line_items", "line_items_latest.csv")
    df.columns = df.columns.str.lower()

    df = df.rename(columns={
        "quantity": "sales_qty",
        "total": "sales_amount"
    })

    df = df[[
        "order_id",
        "order_date_created",
        "order_date_modified",
        "customer_id",
        "order_status",
        "product_id",
        "sales_qty",
        "sales_amount"
    ]]
    return df


def run_all_curated_checks():
    print("=" * 80)
    print("CURATED PROCESSING STARTED")
    print("=" * 80)

    run_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    audit_rows = []

    orders_df = process_orders()
    orders_out = os.path.join(gold_folder, "orders_latest.csv")
    orders_df.to_csv(orders_out, index=False, encoding="utf-8-sig")
    audit_rows.append({
        "run_timestamp": run_timestamp,
        "entity_name": "orders",
        "action": "saved_to_gold",
        "source_file": os.path.join(curated_folder, "orders", "orders_latest.csv"),
        "target_file": orders_out,
        "rows": len(orders_df),
        "columns": len(orders_df.columns),
    })
    print(f"Saved GOLD | orders -> {orders_out}")

    products_df = process_products()
    products_out = os.path.join(gold_folder, "products_latest.csv")
    products_df.to_csv(products_out, index=False, encoding="utf-8-sig")
    audit_rows.append({
        "run_timestamp": run_timestamp,
        "entity_name": "products",
        "action": "saved_to_gold",
        "source_file": os.path.join(curated_folder, "products", "products_latest.csv"),
        "target_file": products_out,
        "rows": len(products_df),
        "columns": len(products_df.columns),
    })
    print(f"Saved GOLD | products -> {products_out}")

    customers_df = process_customers()
    customers_out = os.path.join(gold_folder, "customers_latest.csv")
    customers_df.to_csv(customers_out, index=False, encoding="utf-8-sig")
    audit_rows.append({
        "run_timestamp": run_timestamp,
        "entity_name": "customers",
        "action": "saved_to_gold",
        "source_file": os.path.join(curated_folder, "customers", "customers_latest.csv"),
        "target_file": customers_out,
        "rows": len(customers_df),
        "columns": len(customers_df.columns),
    })
    print(f"Saved GOLD | customers -> {customers_out}")

    line_items_df = process_line_items()
    line_items_out = os.path.join(gold_folder, "line_items_latest.csv")
    line_items_df.to_csv(line_items_out, index=False, encoding="utf-8-sig")
    audit_rows.append({
        "run_timestamp": run_timestamp,
        "entity_name": "line_items",
        "action": "saved_to_gold",
        "source_file": os.path.join(curated_folder, "line_items", "line_items_latest.csv"),
        "target_file": line_items_out,
        "rows": len(line_items_df),
        "columns": len(line_items_df.columns),
    })
    print(f"Saved GOLD | line_items -> {line_items_out}")

    append_audit_log(audit_rows)

    print(f"\nAudit log appended -> {audit_log_path}")
    print("=" * 80)
    print("CURATED PROCESSING FINISHED")
    print("=" * 80)

    return orders_df, products_df, customers_df, line_items_df


if __name__ == "__main__":
    run_all_curated_checks()