from pipelines.base_pipeline import BasePipeline, logger


class OrdersPipeline(BasePipeline):
    def __init__(self, client, config):
        super().__init__(client, config, entity_name="orders", per_page=config.orders_per_page)

    def extract(self):
        logger.info("Extract started | entity=orders")

        page = 1
        watermark = self.get_last_watermark()
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

            original_count = len(rows)

            if watermark:
                rows = [row for row in rows if row.get("date_modified", "") > watermark]

            logger.info(
                "Page processed | entity=orders | page=%s | before=%s | after=%s",
                page,
                original_count,
                len(rows)
            )

            all_rows.extend(rows)

            if original_count < self.per_page:
                break

            page += 1

        self.raw_data = all_rows
        logger.info("Extract finished | entity=orders | total_rows=%s", len(self.raw_data))

    def transform(self):
        logger.info("Transform started | entity=orders | input_rows=%s", len(self.raw_data))

        self.cleaned_data = [
            {
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
            }
            for row in self.raw_data
        ]

        if self.cleaned_data:
            max_modified = max(
                (
                    row.get("date_modified")
                    for row in self.cleaned_data
                    if row.get("date_modified")
                ),
                default=None
            )
            if max_modified:
                self.save_watermark(max_modified)

        logger.info("Transform finished | entity=orders | output_rows=%s", len(self.cleaned_data))