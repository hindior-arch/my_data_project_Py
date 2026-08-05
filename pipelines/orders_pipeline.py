from datetime import datetime
from pathlib import Path
import pandas as pd

from pipelines.base_pipeline import BasePipeline, logger


class OrdersPipeline(BasePipeline):
    def __init__(self, client, config):
        super().__init__(client, config, entity_name="orders", per_page=config.orders_per_page)

    def extract(self):
        logger.info("Extract started | entity=orders")

        page = 1
        # ללא watermark - full load
        all_rows = []

        while True:
            params = {
                "per_page": self.per_page,
                "page": page,
                "orderby": "date",
                "order": "asc",
            }

            rows = self.client.get("orders", params=params)
            if not rows:
                break

            row_count = len(rows)

            logger.info(
                "Page processed | entity=orders | page=%s | rows=%s",
                page,
                row_count
            )

            all_rows.extend(rows)

            if row_count < self.per_page:
                break

            page += 1

        self.raw_data = all_rows
        logger.info("Extract finished | entity=orders | total_rows=%s", len(self.raw_data))

    def transform(self):
        logger.info("Transform started | entity=orders | input_rows=%s", len(self.raw_data))

        self.cleaned_data = []
        self.line_items_data = []

        for row in self.raw_data:
            self.cleaned_data.append({
                "id": row.get("id"),
                "status": row.get("status"),
                "currency": row.get("currency"),
                "date_created": row.get("date_created"),
                "date_modified": row.get("date_modified"),
                "discount_total": row.get("discount_total"),
                "shipping_total": row.get("shipping_total"),
                "total": row.get("total"),
                "customer_id": row.get("customer_id"),
                "payment_method": row.get("payment_method"),
                "payment_method_title": row.get("payment_method_title"),
            })

            for item in row.get("line_items", []):
                self.line_items_data.append({
                    "order_id": row.get("id"),
                    "order_date_created": row.get("date_created"),
                    "order_date_modified": row.get("date_modified"),
                    "customer_id": row.get("customer_id"),
                    "order_status": row.get("status"),
                    "currency": row.get("currency"),
                    "line_item_id": item.get("id"),
                    "product_id": item.get("product_id"),
                    "variation_id": item.get("variation_id"),
                    "name": item.get("name"),
                    "sku": item.get("sku"),
                    "quantity": item.get("quantity"),
                    "price": item.get("price"),
                    "subtotal": item.get("subtotal"),
                    "subtotal_tax": item.get("subtotal_tax"),
                    "total": item.get("total"),
                    "total_tax": item.get("total_tax"),
                    "tax_class": item.get("tax_class"),
                })

        # לא שומרים watermark ב-full load
        logger.info(
            "Transform finished | entity=orders | output_rows=%s | line_items_rows=%s",
            len(self.cleaned_data),
            len(self.line_items_data)
        )

    def load(self):
        logger.info("Load started | entity=%s | rows=%s", self.entity_name, len(self.cleaned_data))

        orders_df = pd.DataFrame(self.cleaned_data)
        line_items_df = pd.DataFrame(self.line_items_data)

        if orders_df.empty:
            logger.warning("No orders to save | entity=%s", self.entity_name)
            return

        # הוספת עמודת זמן טעינה
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        orders_df["extracted_at"] = now_str
        if not line_items_df.empty:
            line_items_df["extracted_at"] = now_str

        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")

        
        # תיקיות נפרדות ל-orders ו-line_items
        orders_raw_dir = Path("data/raw") / "orders"
        line_items_raw_dir = Path("data/raw") / "line_items"
        curated_dir = Path("data/curated") / self.entity_name

        orders_raw_dir.mkdir(parents=True, exist_ok=True)
        line_items_raw_dir.mkdir(parents=True, exist_ok=True)
        curated_dir.mkdir(parents=True, exist_ok=True)

        save_raw_history = getattr(self, "save_raw_history", True)

        # --- היסטוריה (אם רוצים) ---
        if save_raw_history:
            # orders
            raw_csv = raw_dir / f"{self.entity_name}_{timestamp}.csv"
            orders_df.to_csv(raw_csv, index=False, encoding="utf-8-sig")
            logger.info("Raw orders CSV saved | path=%s", raw_csv)

            # line_items
            line_items_raw_csv = raw_dir / f"line_items_{timestamp}.csv"
            line_items_df.to_csv(line_items_raw_csv, index=False, encoding="utf-8-sig")
            logger.info("Raw line items CSV saved | path=%s", line_items_raw_csv)

        # --- קבצים מתעדכנים (latest raw) ---
        # orders_raw.csv
        orders_raw_csv = raw_dir / f"{self.entity_name}_raw.csv"
        orders_df.to_csv(orders_raw_csv, index=False, encoding="utf-8-sig")
        logger.info("Orders raw latest CSV saved | path=%s", orders_raw_csv)

        # line_items_raw.csv
        line_items_raw_csv = raw_dir / "line_items_raw.csv"
        line_items_df.to_csv(line_items_raw_csv, index=False, encoding="utf-8-sig")
        logger.info("Line items raw latest CSV saved | path=%s", line_items_raw_csv)

        # --- curated (orders_latest.csv) ---
        latest_csv = curated_dir / f"{self.entity_name}_latest.csv"
        orders_df.to_csv(latest_csv, index=False, encoding="utf-8-sig")
        logger.info("Latest orders CSV saved | path=%s", latest_csv)