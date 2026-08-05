from pipelines.base_pipeline import BasePipeline, logger
from transforms.privacy import (
    mask_email,
    mask_phone,
    mask_name,
    mask_address,
)


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
                "role": "all",
            }

            rows = self.client.get("customers", params=params)

            if not rows:
                logger.info("No data returned | entity=customers | page=%s", page)
                break

            row_count = len(rows)

            logger.info(
                "Page processed | entity=customers | page=%s | rows=%s",
                page,
                row_count
            )

            all_rows.extend(rows)

            if row_count < self.per_page:
                logger.info("Last page reached | entity=customers | page=%s", page)
                break

            page += 1

        self.raw_data = all_rows
        logger.info("Extract finished | entity=customers | total_rows=%s", len(self.raw_data))

    def transform(self):
        logger.info("Transform started | entity=customers | input_rows=%s", len(self.raw_data))

        self.cleaned_data = [
            {
                "id": row.get("id"),
                "date_created": row.get("date_created"),
                "date_modified": row.get("date_modified"),
                "email": mask_email(row.get("email")),
                "first_name": mask_name(row.get("first_name")),
                "last_name": mask_name(row.get("last_name")),
                "role": row.get("role"),
                "username": row.get("username"),
                "is_paying_customer": row.get("is_paying_customer"),

                "billing_first_name": mask_name((row.get("billing") or {}).get("first_name")),
                "billing_last_name": mask_name((row.get("billing") or {}).get("last_name")),
                "billing_company": (row.get("billing") or {}).get("company"),
                "billing_address_1": mask_address((row.get("billing") or {}).get("address_1")),
                "billing_address_2": mask_address((row.get("billing") or {}).get("address_2")),
                "billing_city": (row.get("billing") or {}).get("city"),
                "billing_state": (row.get("billing") or {}).get("state"),
                "billing_postcode": (row.get("billing") or {}).get("postcode"),
                "billing_country": (row.get("billing") or {}).get("country"),
                # "billing_email": mask_email((row.get("billing") or {}).get("email")),
                "billing_phone": mask_phone((row.get("billing") or {}).get("phone")),
            
            }
            for row in self.raw_data
        ]

        logger.info("Transform finished | entity=customers | output_rows=%s", len(self.cleaned_data))