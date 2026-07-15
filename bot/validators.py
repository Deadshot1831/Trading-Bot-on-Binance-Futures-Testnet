"""Input validation. Every function raises ValueError with a user-readable message."""
import re
from decimal import Decimal, InvalidOperation

SIDES = ("BUY", "SELL")
ORDER_TYPES = ("MARKET", "LIMIT", "STOP")  # STOP = stop-limit on USDT-M futures
_SYMBOL_RE = re.compile(r"^[A-Z0-9]{4,20}$")


def symbol(value):
    value = value.strip().upper()
    if not _SYMBOL_RE.match(value):
        raise ValueError(f"invalid symbol {value!r} (expected something like BTCUSDT)")
    return value


def side(value):
    value = value.strip().upper()
    if value not in SIDES:
        raise ValueError(f"side must be one of {'/'.join(SIDES)}, got {value!r}")
    return value


def order_type(value):
    value = value.strip().upper()
    if value not in ORDER_TYPES:
        raise ValueError(f"order type must be one of {'/'.join(ORDER_TYPES)}, got {value!r}")
    return value


def positive_decimal(value, name):
    if value is None:
        raise ValueError(f"{name} is required for this order type")
    try:
        number = Decimal(str(value).strip())
    except InvalidOperation:
        raise ValueError(f"{name} must be a number, got {value!r}") from None
    if number <= 0:
        raise ValueError(f"{name} must be positive, got {number}")
    return number
