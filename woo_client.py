import requests
from requests.auth import HTTPBasicAuth
from config import (
    WOO_BASE_URL,
    WOO_CONSUMER_KEY,
    WOO_CONSUMER_SECRET,
    REQUEST_TIMEOUT,
    PRODUCTS_PER_PAGE,
    ORDERS_PER_PAGE,
)


def _validate_config():
    if not WOO_BASE_URL:
        raise ValueError("Missing WOO_BASE_URL in .env")
    if not WOO_CONSUMER_KEY:
        raise ValueError("Missing WOO_CONSUMER_KEY in .env")
    if not WOO_CONSUMER_SECRET:
        raise ValueError("Missing WOO_CONSUMER_SECRET in .env")


def _get(endpoint, params=None):
    _validate_config()

    url = f"{WOO_BASE_URL}/wp-json/wc/v3/{endpoint}"

    response = requests.get(
        url,
        auth=HTTPBasicAuth(WOO_CONSUMER_KEY, WOO_CONSUMER_SECRET),
        params=params,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()


def get_products(per_page=PRODUCTS_PER_PAGE, page=1):
    return _get("products", params={"per_page": per_page, "page": page})


def get_orders(per_page=ORDERS_PER_PAGE, page=1, status=None):
    params = {"per_page": per_page, "page": page}

    if status:
        params["status"] = status

    return _get("orders", params=params)


def test_connection():
    products = get_products(per_page=1)
    return len(products)