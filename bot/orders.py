"""Order construction and placement."""
import logging

from . import validators

log = logging.getLogger(__name__)


def build_order(symbol, side, order_type, quantity, price=None, stop_price=None):
    """Validate inputs and return the parameter dict for POST /fapi/v1/order."""
    symbol = validators.symbol(symbol)
    side = validators.side(side)
    order_type = validators.order_type(order_type)
    quantity = validators.positive_decimal(quantity, "quantity")

    params = {
        "symbol": symbol,
        "side": side,
        "type": order_type,
        "quantity": format(quantity, "f"),
    }

    if order_type == "MARKET":
        if price is not None or stop_price is not None:
            raise ValueError("price/stop-price are not valid for MARKET orders")
        return params

    params["price"] = format(validators.positive_decimal(price, "price"), "f")
    params["timeInForce"] = "GTC"

    if order_type == "STOP":
        params["stopPrice"] = format(validators.positive_decimal(stop_price, "stop-price"), "f")
    elif stop_price is not None:
        raise ValueError("stop-price is only valid for STOP orders")
    return params


def place_order(client, params):
    log.info("Placing order: %s", params)
    response = client.place_order(**params)
    log.info(
        "Order accepted: orderId=%s status=%s executedQty=%s avgPrice=%s",
        response.get("orderId"), response.get("status"),
        response.get("executedQty"), response.get("avgPrice"),
    )
    return response
