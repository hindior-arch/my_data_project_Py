from dotenv import load_dotenv
import os

load_dotenv()


class WooConfig:
    def __init__(self):
        self.base_url = os.getenv("WOO_BASE_URL", "").rstrip("/")
        self.consumer_key = os.getenv("WOO_CONSUMER_KEY", "")
        self.consumer_secret = os.getenv("WOO_CONSUMER_SECRET", "")
        self.request_timeout = int(os.getenv("REQUEST_TIMEOUT", 20))
        self.products_per_page = int(os.getenv("PRODUCTS_PER_PAGE", 10))
        self.orders_per_page = int(os.getenv("ORDERS_PER_PAGE", 10))
        self.customers_per_page = int(os.getenv("CUSTOMERS_PER_PAGE", 10))
        self.save_excel = os.getenv("SAVE_EXCEL", "true").lower() == "true"

        self.validate()

    def validate(self):
        missing = []

        if not self.base_url:
            missing.append("WOO_BASE_URL")
        if not self.consumer_key:
            missing.append("WOO_CONSUMER_KEY")
        if not self.consumer_secret:
            missing.append("WOO_CONSUMER_SECRET")

        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}"
            )