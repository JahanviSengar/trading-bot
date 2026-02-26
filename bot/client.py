"""
Binance Futures Testnet REST API client.
Handles request signing, authentication, and HTTP calls.
"""

import hashlib
import hmac
import time
from urllib.parse import urlencode

import requests

from bot.logging_config import get_logger

logger = get_logger(__name__)

BASE_URL = "https://testnet.binancefuture.com"


class BinanceClient:
    def __init__(self, api_key: str, api_secret: str):
        if not api_key or not api_secret:
            raise ValueError("API key and secret must not be empty.")
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = requests.Session()
        self.session.headers.update({"X-MBX-APIKEY": self.api_key})

    def _sign(self, params: dict) -> dict:
        """Append HMAC-SHA256 signature to params."""
        params["timestamp"] = int(time.time() * 1000)
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        params["signature"] = signature
        return params

    def _request(self, method: str, endpoint: str, params: dict) -> dict:
        """Send a signed request and return the JSON response."""
        signed_params = self._sign(params)
        url = f"{BASE_URL}{endpoint}"
        logger.debug("Request: %s %s params=%s", method, url, signed_params)

        try:
            response = self.session.request(method, url, params=signed_params, timeout=10)
            response.raise_for_status()
            data = response.json()
            logger.debug("Response: %s", data)
            return data
        except requests.exceptions.HTTPError as exc:
            error_body = exc.response.json() if exc.response is not None else {}
            logger.error("HTTP error %s: %s", exc.response.status_code, error_body)
            raise RuntimeError(
                f"Binance API error {error_body.get('code')}: {error_body.get('msg', str(exc))}"
            ) from exc
        except requests.exceptions.RequestException as exc:
            logger.error("Request failed: %s", exc)
            raise RuntimeError(f"Network error: {exc}") from exc

    def new_order(self, params: dict) -> dict:
        """POST /fapi/v1/order"""
        return self._request("POST", "/fapi/v1/order", params)

    def get_exchange_info(self) -> dict:
        """GET /fapi/v1/exchangeInfo (no signature required)."""
        url = f"{BASE_URL}/fapi/v1/exchangeInfo"
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as exc:
            raise RuntimeError(f"Failed to fetch exchange info: {exc}") from exc
