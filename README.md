# Trading Bot — Binance Futures Testnet (USDT-M)

A small Python CLI that places **MARKET**, **LIMIT**, and **STOP-LIMIT** orders on the
[Binance Futures Testnet](https://testnet.binancefuture.com), with input validation,
structured logging, and clean error handling.

## Structure

```
bot/
  client.py          # signed REST client (HMAC-SHA256, error handling)
  orders.py          # order construction + placement
  validators.py      # input validation
  logging_config.py  # file + console logging
cli.py               # argparse entry point
test_bot.py          # offline self-check (no keys/network needed)
logs/bot.log         # API requests, responses, and errors
```

## Setup

1. Register at <https://testnet.binancefuture.com> and generate an API key/secret
   (API Key tab at the bottom of the testnet UI).
2. Install:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Export credentials:

```bash
export BINANCE_API_KEY="your_testnet_key"
export BINANCE_API_SECRET="your_testnet_secret"
```

## Usage

```bash
# MARKET order
python cli.py BTCUSDT BUY MARKET 0.002

# LIMIT order (price required)
python cli.py BTCUSDT SELL LIMIT 0.002 --price 120000

# STOP-LIMIT order (bonus): triggers a limit order when stop-price is hit
python cli.py BTCUSDT SELL STOP 0.002 --price 95000 --stop-price 96000
```

The CLI prints the order request summary, then the response details
(`orderId`, `status`, `executedQty`, `avgPrice`, …) with a SUCCESS/FAILED message.
Every API request, response, and error is logged to `logs/bot.log`.

Exit codes: `0` success, `1` API/network failure, `2` invalid input or missing credentials.

## Self-check

```bash
python test_bot.py   # validates signing + input validation offline
```

## Assumptions

- **Testnet only** — base URL is hard-coded to `https://testnet.binancefuture.com`.
- Credentials come from environment variables (never from files or CLI args, so they
  can't leak into shell history or the repo).
- `STOP` is Binance's stop-limit type on USDT-M futures (`--stop-price` triggers a limit
  order at `--price`); `timeInForce` is fixed to GTC for LIMIT/STOP orders. Since
  Binance's 2025-12-09 API migration, STOP orders are sent to the Algo Order endpoint
  (`/fapi/v1/algoOrder`, `algoType=CONDITIONAL`, `triggerPrice`) and return an
  `algoId`/`algoStatus` instead of `orderId`/`status`.
- Quantity/price precision is validated by the exchange (per-symbol filters like
  `LOT_SIZE`/`PRICE_FILTER` are enforced server-side and reported back as clear errors).
- If you see error `-1021` (timestamp outside recvWindow), sync your system clock.
