import requests
from requests.auth import HTTPBasicAuth
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from logging_config import setup_logger

logger = setup_logger()


class WooClient:
    def __init__(self, config):
        self.config = config
        self.session = self._create_session()

        logger.info("WooClient initialized | base_url=%s", self.config.base_url)

    def _create_session(self):
        session = requests.Session()
        session.auth = HTTPBasicAuth(
            self.config.consumer_key,
            self.config.consumer_secret
        )

        retry_strategy = Retry(
            total=3,
            connect=3,
            read=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        return session

    def _build_url(self, endpoint):
        return f"{self.config.base_url}/wp-json/wc/v3/{endpoint}"

    def get(self, endpoint, params=None):
        url = self._build_url(endpoint)
        params = params or {}

        logger.info("GET started | endpoint=%s | params=%s", endpoint, params)

        try:
            response = self.session.get(
                url,
                params=params,
                timeout=self.config.request_timeout
            )
            response.raise_for_status()

            logger.info(
                "GET succeeded | endpoint=%s | status_code=%s",
                endpoint,
                response.status_code
            )
            return response.json()

        except requests.exceptions.Timeout:
            logger.exception(
                "Timeout error | endpoint=%s | timeout=%s",
                endpoint,
                self.config.request_timeout
            )
            raise

        except requests.exceptions.ConnectionError:
            logger.exception("Connection error | endpoint=%s", endpoint)
            raise

        except requests.exceptions.HTTPError:
            logger.exception(
                "HTTP error | endpoint=%s | status_code=%s",
                endpoint,
                getattr(response, "status_code", "unknown")
            )
            raise

        except Exception:
            logger.exception("Unexpected error | endpoint=%s", endpoint)
            raise

    def test_connection(self):
        logger.info("Testing API connection")
        products = self.get("products", params={"per_page": 1, "page": 1})
        logger.info("API connection test passed | rows=%s", len(products))
        return len(products)