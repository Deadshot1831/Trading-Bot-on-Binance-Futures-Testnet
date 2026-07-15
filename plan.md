# Plan — Simplified Trading Bot (Binance Futures Testnet, USDT-M)

## Goal
CLI app that places MARKET / LIMIT (and STOP-LIMIT as bonus) orders on
`https://testnet.binancefuture.com`, with validation, logging, and clean errors.

## Stack decisions
- **Python 3 + `requests`** (direct REST, HMAC-SHA256 signing) — one dependency,
  no python-binance needed for 2 endpoints.
- **argparse** for CLI — stdlib, no Typer/Click dependency.
- **`logging`** stdlib — file (`logs/bot.log`, DEBUG) + console (INFO).
- **`Decimal`** for quantity/price — no float formatting surprises in signed params.
- API keys via `BINANCE_API_KEY` / `BINANCE_API_SECRET` env vars.

## Structure
```
bot/
  __init__.py
  client.py          # FuturesClient: signing, request/response/error handling
  orders.py          # build + place order params (MARKET / LIMIT / STOP-LIMIT)
  validators.py      # symbol/side/type/quantity/price validation
  logging_config.py  # file + console logging setup
cli.py               # argparse entry point, prints summary + result
test_bot.py          # self-check: known HMAC vector + validator cases
README.md            # setup, examples, assumptions
requirements.txt     # requests
logs/                # bot.log (runtime), committed sample order logs
```

## Tasks
- [x] plan.md (this file)
- [x] `bot/` package: client, orders, validators, logging_config
- [x] `cli.py` entry point
- [x] `test_bot.py` self-check (runs offline, no keys needed)
- [x] README.md + requirements.txt + .gitignore
- [x] Place one MARKET + one LIMIT order on testnet (needs user's API keys) and
      commit the resulting log files

## Bonus chosen
STOP-LIMIT order type (`type=STOP`, `stopPrice` + `price`) — smallest useful third type.

## Error handling
- Input errors → validators raise `ValueError`, CLI prints message, exit 2.
- API errors (non-2xx, Binance `{code, msg}`) → `BinanceAPIError`, exit 1.
- Network failures (`requests.RequestException`) → logged + friendly message, exit 1.

## Out of scope (deliberately)
WebSocket streams, order cancellation/query, position management, config files,
retry logic — not asked for.
