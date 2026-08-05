import pandas as pd
from pathlib import Path


PROJECT_ROOT = Path(r"D:\Project\Naya\Py_env")

folder_path = PROJECT_ROOT / "data" / "raw"
log_dir = PROJECT_ROOT / "logs"


def run_all_raw_checks():
    if folder_path.exists():
        print("subfolders in data/raw:")
        for p in folder_path.iterdir():
            print("  -", p.name, "| dir:", p.is_dir())

    entity_folders = ["orders", "products", "customers", "line_items"]

    print("\n" + "=" * 80)
    print("VALIDATION RESULTS")
    print("=" * 80)

    df_list = []
    df_dict = {}
    file_metadata = []

    for entity in entity_folders:
        entity_dir = folder_path / entity
        raw_file = entity_dir / f"{entity}_raw.csv"

        print(f"\n{entity}:")
        print(f"  dir exists? {entity_dir.exists()}")
        print(f"  raw_file path: {raw_file}")
        print(f"  raw_file exists? {raw_file.exists()}")

        if entity_dir.exists():
            csv_files = list(entity_dir.glob("*.csv"))
            print(f"  CSV files in {entity}/:")
            for f in csv_files:
                print(f"    - {f.name} ({f.stat().st_size} bytes)")

        file_path = folder_path / entity / f"{entity}_raw.csv"

        try:
            df = pd.read_csv(file_path)

            # שמירה לבדיקות ידניות
            df_list.append(df)
            df_dict[entity] = df

            # ולידציית Null בסיסית
            total_nulls = df.isnull().sum().sum()
            null_percentage = (
                round((total_nulls / (len(df) * len(df.columns))) * 100, 2)
                if len(df) > 0
                else 0
            )

            # עמודת תאריך אחת לסיכום
            date_created = None

            if entity in ["orders", "products"]:
                if "date_created" in df.columns:
                    date_created = df["date_created"].max()
            elif entity == "line_items":
                if "order_date_created" in df.columns:
                    date_created = df["order_date_created"].max()
            # customers → date_created נשאר None

            # --- בדיקת כפילויות ---
            duplicate_status = "valid"

            if entity == "orders":
                dup_count = df.duplicated(subset=["id"]).sum()
                duplicate_status = "invalid" if dup_count > 0 else "valid"
            elif entity == "line_items":
                dup_count = df.duplicated(subset=["order_id", "line_item_id"]).sum()
                duplicate_status = "invalid" if dup_count > 0 else "valid"
            elif entity == "products":
                dup_count = df.duplicated(subset=["id"]).sum()
                duplicate_status = "invalid" if dup_count > 0 else "valid"
            elif entity == "customers":
                dup_count = df.duplicated(subset=["id"]).sum()
                duplicate_status = "invalid" if dup_count > 0 else "valid"

            # --- בדיקת טווחי תאריכים ---
            date_range_status = "valid"

            if entity in ["orders", "products"]:
                date_col = "date_created"
            elif entity == "line_items":
                date_col = "order_date_created"
            else:
                date_col = None

            if date_col and date_col in df.columns:
                df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
                max_date = df[date_col].max()
                min_date = df[date_col].min()

                max_allowed = pd.Timestamp("2026-08-06")
                min_allowed = pd.Timestamp("2019-06-01")

                if pd.notna(max_date) and (
                    max_date > max_allowed or min_date < min_allowed
                ):
                    date_range_status = "invalid"

            # --- בדיקת טווחי ערכים (measures) ---
            measures_status = "valid"

            if entity == "orders":
                if "total" in df.columns and (df["total"] < 0).any():
                    measures_status = "invalid"

            elif entity == "line_items":
                if "total" in df.columns and (df["total"] < 0).any():
                    measures_status = "invalid"
                if "quantity" in df.columns and (df["quantity"] <= 0).any():
                    measures_status = "invalid"
                if "price" in df.columns and (df["price"] < 0).any():
                    measures_status = "invalid"

            elif entity == "products":
                if "price" in df.columns and (df["price"] < 0).any():
                    measures_status = "invalid"

            # customers: אין בדיקה

            metadata = {
                "entity_name": entity,
                "rows": len(df),
                "columns": len(df.columns),
                "extracted_at": df["extracted_at"].max()
                if "extracted_at" in df.columns
                else None,
                "total_nulls": total_nulls,
                "null_percentage": null_percentage,
                "date_created": date_created,
                "duplicate_status": duplicate_status,
                "date_range_status": date_range_status,
                "measures_status": measures_status,
            }

        except FileNotFoundError:
            metadata = {
                "entity_name": entity,
                "rows": 0,
                "columns": 0,
                "extracted_at": None,
                "total_nulls": 0,
                "null_percentage": 0,
                "date_created": None,
                "duplicate_status": "invalid",
                "date_range_status": "invalid",
                "measures_status": "invalid",
            }

        file_metadata.append(metadata)

    df_summary = pd.DataFrame(file_metadata)

    print(
        df_summary[
            [
                "entity_name",
                "rows",
                "columns",
                "extracted_at",
                "total_nulls",
                "null_percentage",
                "date_created",
                "duplicate_status",
                "date_range_status",
                "measures_status",
            ]
        ].to_string(index=False)
    )

    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "validations_raw.csv"
    df_summary.to_csv(log_path, index=False, encoding="utf-8")

    print(f"\nValidation summary saved to: {log_path}")

    print("\n" + "=" * 80)
    print("DATAFRAMES FOR MANUAL INSPECTION")
    print("=" * 80)
    print("Use df_dict['entity_name'] or df_list[index]")
    print(f"Available: {list(df_dict.keys())}")

    return df_summary, df_list, df_dict


if __name__ == "__main__":
    run_all_raw_checks()