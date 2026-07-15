#!/usr/bin/env python3
"""Place MARKET / LIMIT / STOP-LIMIT orders on Binance USDT-M Futures testnet.

Examples:
  export BINANCE_API_KEY=... BINANCE_API_SECRET=...
  python cli.py BTCUSDT BUY MARKET 0.002
  python cli.py BTCUSDT SELL LIMIT 0.002 --price 120000
  python cli.py BTCUSDT SELL STOP 0.002 --price 95000 --stop-price 96000
"""
import argparse
import logging
import os
import sys

import requests

from bot.client import BinanceAPIError, FuturesClient
from bot.logging_config import setup_logging
from bot.orders import build_order, place_order

log = logging.getLogger("cli")

RESPONSE_FIELDS = (
    "orderId", "symbol", "side", "type", "status",
    "origQty", "executedQty", "avgPrice", "price", "stopPrice",
)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Place an order on Binance USDT-M Futures testnet.",
        epilog="API credentials are read from BINANCE_API_KEY / BINANCE_API_SECRET.",
    )
    parser.add_argument("symbol", help="trading pair, e.g. BTCUSDT")
    parser.add_argument("side", help="BUY or SELL")
    parser.add_argument("type", help="MARKET, LIMIT or STOP (stop-limit)")
    parser.add_argument("quantity", help="order quantity in the base asset")
    parser.add_argument("--price", help="limit price (required for LIMIT and STOP)")
    parser.add_argument("--stop-price", help="trigger price (required for STOP)")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    setup_logging()

    api_key = os.environ.get("BINANCE_API_KEY")
    api_secret = os.environ.get("BINANCE_API_SECRET")
    if not api_key or not api_secret:
        print("ERROR: set BINANCE_API_KEY and BINANCE_API_SECRET environment variables")
        return 2

    try:
        params = build_order(
            args.symbol, args.side, args.type, args.quantity,
            price=args.price, stop_price=args.stop_price,
        )
    except ValueError as exc:
        log.error("Invalid input: %s", exc)
        print(f"Invalid input: {exc}")
        return 2

    print("Order request:")
    for key, value in params.items():
        print(f"  {key:14}{value}")

    try:
        response = place_order(FuturesClient(api_key, api_secret), params)
    except BinanceAPIError as exc:
        print(f"FAILED: Binance rejected the order — {exc.msg} (code {exc.code})")
        return 1
    except requests.RequestException as exc:
        print(f"FAILED: network error — {exc}")
        return 1

    print("SUCCESS — order placed:")
    for key in RESPONSE_FIELDS:
        if key in response:
            print(f"  {key:14}{response[key]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
