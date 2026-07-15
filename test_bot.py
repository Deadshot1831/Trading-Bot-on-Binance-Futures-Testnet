"""Offline self-check — run `python3 test_bot.py`. No API keys or network needed."""
import hashlib
import hmac

from bot.client import FuturesClient
from bot.orders import build_order


def rejects(**kwargs):
    try:
        build_order(**kwargs)
    except ValueError:
        return True
    return False


# --- signing: query string built in param order, HMAC-SHA256 of it appended ---
secret = "testsecret"
client = FuturesClient("testkey", secret)
params = {"symbol": "BTCUSDT", "side": "BUY", "type": "MARKET", "quantity": "0.002"}
query = "symbol=BTCUSDT&side=BUY&type=MARKET&quantity=0.002"
sig = hmac.new(secret.encode(), query.encode(), hashlib.sha256).hexdigest()
assert client._sign(params) == f"{query}&signature={sig}"

# --- valid orders ---
p = build_order("btcusdt", "buy", "market", "0.002")
assert p == {"symbol": "BTCUSDT", "side": "BUY", "type": "MARKET", "quantity": "0.002"}

p = build_order("BTCUSDT", "SELL", "LIMIT", "0.002", price="120000")
assert p["price"] == "120000" and p["timeInForce"] == "GTC"

p = build_order("BTCUSDT", "SELL", "STOP", "0.002", price="95000", stop_price="96000")
assert p["triggerPrice"] == "96000" and p["price"] == "95000"
assert p["algoType"] == "CONDITIONAL"  # STOP orders route to /fapi/v1/algoOrder

# --- invalid orders ---
assert rejects(symbol="BTCUSDT", side="SELL", order_type="LIMIT", quantity="1")  # no price
assert rejects(symbol="BTCUSDT", side="HOLD", order_type="MARKET", quantity="1")
assert rejects(symbol="BTCUSDT", side="BUY", order_type="MARKET", quantity="-1")
assert rejects(symbol="BTCUSDT", side="BUY", order_type="MARKET", quantity="abc")
assert rejects(symbol="BTC/USDT", side="BUY", order_type="MARKET", quantity="1")
assert rejects(symbol="BTCUSDT", side="BUY", order_type="MARKET", quantity="1", price="5")
assert rejects(symbol="BTCUSDT", side="SELL", order_type="STOP", quantity="1", price="95000")  # no stop
assert rejects(symbol="BTCUSDT", side="SELL", order_type="LIMIT", quantity="1", price="95000",
               stop_price="96000")  # stop-price on LIMIT

print("all checks passed")
