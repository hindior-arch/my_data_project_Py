from pipelines.base_pipeline import BasePipeline, logger


class ProductsPipeline(BasePipeline):
    def __init__(self, client, config):
        super().__init__(client, config, entity_name="products", per_page=config.products_per_page)

    def extract(self):
        logger.info("Extract started | entity=products")

        page = 1
        all_rows = []

        while True:
            params = {
                "per_page": self.per_page,
                "page": page,
                "orderby": "id",
                "order": "asc",
            }

            rows = self.client.get("products", params=params)

            if not rows:
                logger.info("No data returned | entity=products | page=%s", page)
                break

            row_count = len(rows)

            logger.info(
                "Page processed | entity=products | page=%s | rows=%s",
                page,
                row_count
            )

            all_rows.extend(rows)

            if row_count < self.per_page:
                logger.info("Last page reached | entity=products | page=%s", page)
                break

            page += 1

        self.raw_data = all_rows
        logger.info("Extract finished | entity=products | total_rows=%s", len(self.raw_data))

    def transform(self):
        logger.info("Transform started | entity=products | input_rows=%s", len(self.raw_data))

        self.cleaned_data = [
            {
                "id": row.get("id"),
                "name": row.get("name"),
                "slug": row.get("slug"),
                "type": row.get("type"),
                "status": row.get("status"),
                "featured": row.get("featured"),
                "catalog_visibility": row.get("catalog_visibility"),
                "price": row.get("price"),
                "regular_price": row.get("regular_price"),
                "sale_price": row.get("sale_price"),
                "on_sale": row.get("on_sale"),
                "stock_status": row.get("stock_status"),
                "stock_quantity": row.get("stock_quantity"),
                "sku": row.get("sku"),
                "date_created": row.get("date_created"),
                "date_modified": row.get("date_modified"),
            }
            for row in self.raw_data
        ]

        logger.info("Transform finished | entity=products | output_rows=%s", len(self.cleaned_data))