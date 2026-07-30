from dotenv import load_dotenv
import os

load_dotenv()

WOO_BASE_URL = os.getenv("WOO_BASE_URL")
WOO_CONSUMER_KEY = os.getenv("WOO_CONSUMER_KEY")
WOO_CONSUMER_SECRET = os.getenv("WOO_CONSUMER_SECRET")

REQUEST_TIMEOUT = 20
PRODUCTS_PER_PAGE = 10
ORDERS_PER_PAGE = 10