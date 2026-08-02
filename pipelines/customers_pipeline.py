from pipelines.base_pipeline import BasePipeline, logger


class CustomersPipeline(BasePipeline):
    def __init__(self, client, config):
        super().__init__(client, config, entity_name="customers", per_page=config.customers_per_page)

    def extract(self):
        logger.info("Extract started | entity=customers")

        page = 1
        all_rows = []

        while True:
            params = {
                "per_page": self.per_page,
                "page": page,
                "orderby": "id",
                "order": "asc",
            }

            rows = self.client.get("customers", params=params)
            logger.info("Customers API returned | page=%s | rows=%s", page, len(rows) if rows else 0)

            if not rows:
                break

            all_rows.extend(rows)

            logger.info(
                "Page processed | entity=customers | page=%s | rows=%s",
                page,
                len(rows)
            )

            if len(rows) < self.per_page:
                break

            page += 1

        self.raw_data = all_rows
        logger.info("Extract finished | entity=customers | total_rows=%s", len(self.raw_data))

    def transform(self):
        logger.info("Transform started | entity=customers | input_rows=%s", len(self.raw_data))

        self.cleaned_data = []

        for row in self.raw_data:
            billing = row.get("billing", {}) or row.get("billing_address", {})
            shipping = row.get("shipping", {}) or row.get("shipping_address", {})

            self.cleaned_data.append({
                "id": row.get("id"),
                "email": row.get("email"),
                "first_name": row.get("first_name"),
                "last_name": row.get("last_name"),
                "username": row.get("username"),
                "date_created": row.get("date_created"),

                "billing_first_name": billing.get("first_name"),
                "billing_last_name": billing.get("last_name"),
                "billing_company": billing.get("company"),
                "billing_address_1": billing.get("address_1"),
                "billing_address_2": billing.get("address_2"),
                "billing_city": billing.get("city"),
                "billing_state": billing.get("state"),
                "billing_postcode": billing.get("postcode"),
                "billing_country": billing.get("country"),
                "billing_email": billing.get("email"),
                "billing_phone": billing.get("phone"),

            })

        logger.info("Transform finished | entity=customers | output_rows=%s", len(self.cleaned_data))