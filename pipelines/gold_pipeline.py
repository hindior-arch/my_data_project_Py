import pandas as pd
from pathlib import Path
from datetime import datetime

# נתיבים
folder_path = Path("D:/Project/Naya/Py_env/data")
folder_path_gold = folder_path / "gold"


file_pathordersline = folder_path / "curated" / "line_items" / "line_items_latest.csv"
file_pathordersheader = folder_path / "curated" / "orders" / "orders_latest.csv"
file_pathproducts = folder_path / "curated" / "products" / "products_latest.csv"
file_pathcustomers = folder_path / "curated" / "customers" / "customers_latest.csv"

file_pathfactable = folder_path_gold / "facttable.csv"


# טעינת הטבלאות
dfordersline = pd.read_csv(file_pathordersline)
dfordersheader = pd.read_csv(file_pathordersheader)
dfproducts = pd.read_csv(file_pathproducts)
dfcustomers = pd.read_csv(file_pathcustomers)

# עמודות שרוצים להוסיף מטבלת Orders
ordersheader_columns = [
    "order_id",
    "payment_method_title"
]

# עמודות שרוצים להוסיף מטבלת products
products_columns = [
    "product_id",
    "product_name",
    "product_status",
    "product_price",
    "product_date_created"
]



# עמודות שרוצים להוסיף מטבלת products
customers_columns = [
    "customer_id",
    "email",
    "billing_city",
    "customer_date_created",
    "customer_date_modified"
]

# חיבור Ordersheader  אל Ordersline ==> Create new dffact
dffacttable = dfordersline.merge(
    dfordersheader[ordersheader_columns],
    on="order_id",
    how="left",
    validate="many_to_one"
)

# חיבור Products  אל new dffact ==> Create new dffact
dffacttable = dffacttable.merge(
    dfproducts[products_columns],
    on="product_id",
    how="left",
    validate="many_to_one"
)

# חיבור Products  אל new dffact ==> Create new dffact
dffacttable = dffacttable.merge(
    dfcustomers[customers_columns],
    on="customer_id",
    how="left",
    validate="many_to_one"
)

# יצירת תיקיית gold אם אינה קיימת
folder_path_gold.mkdir(parents=True, exist_ok=True)

# שמירת Fact Table
dffacttable.to_csv(
    file_pathfactable,
    index=False,
    encoding="utf-8-sig"
)

# תיקיית logs בשורש הפרויקט
project_dir = folder_path_gold.parent.parent
log_dir = project_dir / "logs"
log_dir.mkdir(parents=True, exist_ok=True)

# קובץ לוג מצטבר
log_path = log_dir / "logcreationfacttable.csv"

# יצירת רשומת לוג אחת
log_row = pd.DataFrame([{
    "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "file_name": file_pathfactable.name,
    "file_path": str(file_pathfactable.resolve()),
    "rows": len(dffacttable),
    "columns": len(dffacttable.columns),
    "file_exists": file_pathfactable.exists(),
    "file_size_bytes": file_pathfactable.stat().st_size
}])

# הוספת הרשומה ללוג בלי למחוק הרצות קודמות
log_row.to_csv(
    log_path,
    mode="a",
    header=not log_path.exists(),
    index=False,
    encoding="utf-8-sig"
)

# פלט לטרמינל
print("\n" + "=" * 80)
print("Create Fact Table csv")
print("=" * 80)
print(f"Fact table saved to: {file_pathfactable.resolve()}")
print(f"Fact table exists: {file_pathfactable.exists()}")
print(f"Rows: {len(dffacttable)}")
print(f"Columns: {len(dffacttable.columns)}")
print(f"Creation log saved to: {log_path.resolve()}")


