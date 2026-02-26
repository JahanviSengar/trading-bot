"""
Order construction and placement logic.
Supports MARKET, LIMIT, and STOP-LIMIT orders.
"""

from bot.client import BinanceClient
from bot.logging_config import get_logger
from bot.validators import (
    validate_order_type,
    validate_price,
    validate_quantity,
    validate_side,
    validate_symbol,
    validate_time_in_force,
)

logger = get_logger(__name__)


def _build_params(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: str | None = None,
    stop_price: str | None = None,
    time_in_force: str | None = None,
) -> dict:
    """Build the request parameter dict based on order type."""
    params: dict = {
        "symbol": symbol,
        "side": side,
        "type": order_type,
        "quantity": quantity,
    }

    if order_type == "MARKET":
        # MARKET orders do not require price or timeInForce
        pass

    elif order_type == "LIMIT":
        if price is None:
            raise ValueError("LIMIT orders require --price.")
        params["price"] = validate_price(price, "price")
        params["timeInForce"] = validate_time_in_force(time_in_force or "GTC")

    elif order_type == "STOP":
        # Stop-Limit order: requires both price (limit price) and stop_price
        if price is None or stop_price is None:
            raise ValueError(
                "STOP orders require both --price (limit price) and --stop-price."
            )
        params["price"] = validate_price(price, "price")
        params["stopPrice"] = validate_price(stop_price, "stop_price")
        params["timeInForce"] = validate_time_in_force(time_in_force or "GTC")

    return params


def place_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: str | None = None,
    stop_price: str | None = None,
    time_in_force: str | None = None,
) -> dict:
    """Validate inputs, build params, and submit the order."""
    symbol = validate_symbol(symbol)
    side = validate_side(side)
    order_type = validate_order_type(order_type)
    quantity = validate_quantity(quantity)

    params = _build_params(
        symbol=symbol,
        side=side,
        order_type=order_type,
        quantity=quantity,
        price=price,
        stop_price=stop_price,
        time_in_force=time_in_force,
    )

    logger.info(
        "Placing %s %s order | symbol=%s qty=%s price=%s stopPrice=%s",
        side,
        order_type,
        symbol,
        quantity,
        price,
        stop_price,
    )

    response = client.new_order(params)
    logger.info("Order placed successfully | orderId=%s", response.get("orderId"))
    return response


def print_order_summary(args_namespace) -> None:
    """Print a human-readable summary of the order *before* submission."""
    lines = [
        "",
        "═" * 50,
        "          ORDER SUMMARY (pre-submission)",
        "═" * 50,
        f"  Symbol     : {args_namespace.symbol.upper()}",
        f"  Side       : {args_namespace.side.upper()}",
        f"  Type       : {args_namespace.type.upper()}",
        f"  Quantity   : {args_namespace.quantity}",
    ]
    if args_namespace.price:
        lines.append(f"  Price      : {args_namespace.price}")
    if hasattr(args_namespace, "stop_price") and args_namespace.stop_price:
        lines.append(f"  Stop Price : {args_namespace.stop_price}")
    if args_namespace.time_in_force:
        lines.append(f"  TIF        : {args_namespace.time_in_force}")
    lines.append("═" * 50)
    print("\n".join(lines))


def print_order_response(response: dict) -> None:
    """Print key fields from Binance order response."""
    print("\n" + "═" * 50)
    print("          ORDER RESPONSE")
    print("═" * 50)
    print(f"  Order ID      : {response.get('orderId', 'N/A')}")
    print(f"  Status        : {response.get('status', 'N/A')}")
    print(f"  Executed Qty  : {response.get('executedQty', 'N/A')}")
    print(f"  Avg Price     : {response.get('avgPrice', 'N/A')}")
    print(f"  Symbol        : {response.get('symbol', 'N/A')}")
    print(f"  Side          : {response.get('side', 'N/A')}")
    print(f"  Type          : {response.get('type', 'N/A')}")
    print(f"  Client OID    : {response.get('clientOrderId', 'N/A')}")
    print(f"  Update Time   : {response.get('updateTime', 'N/A')}")
    print("═" * 50 + "\n")
