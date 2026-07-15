"""Signed REST client for Binance USDT-M Futures testnet."""
import hashlib
import hmac
import logging
import time
from urllib.parse import urlencode

import requests

log = logging.getLogger(__name__)

BASE_URL = "https://testnet.binancefuture.com"
RECV_WINDOW = 5000


class BinanceAPIError(Exception):
    """Non-2xx response from Binance (carries the API's {code, msg} payload)."""

    def __init__(self, status, code, msg):
        self.status = status
        self.code = code
        self.msg = msg
        super().__init__(f"HTTP {status} / code {code}: {msg}")


class FuturesClient:
    def __init__(self, api_key, api_secret, base_url=BASE_URL, timeout=10):
        self._secret = api_secret.encode()
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers["X-MBX-APIKEY"] = api_key

    def _sign(self, params):
        query = urlencode(params)
        signature = hmac.new(self._secret, query.encode(), hashlib.sha256).hexdigest()
        return f"{query}&signature={signature}"

    def _signed_request(self, method, path, params):
        params = {k: v for k, v in params.items() if v is not None}
        params["recvWindow"] = RECV_WINDOW
        params["timestamp"] = int(time.time() * 1000)

        log.info("REQUEST %s %s %s", method, path, params)
        try:
            resp = self.session.request(
                method,
                self.base_url + path,
                data=self._sign(params),
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=self.timeout,
            )
        except requests.RequestException:
            log.exception("NETWORK ERROR %s %s", method, path)
            raise
        log.info("RESPONSE %s %s -> %s %s", method, path, resp.status_code, resp.text)

        if resp.ok:
            return resp.json()
        try:
            body = resp.json()
        except ValueError:
            body = {}
        error = BinanceAPIError(resp.status_code, body.get("code"), body.get("msg", resp.text))
        log.error("API ERROR %s %s: %s", method, path, error)
        raise error

    def place_order(self, **params):
        return self._signed_request("POST", "/fapi/v1/order", params)
