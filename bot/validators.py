"""
Input validators for CLI arguments.
"""

import re

VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP"}
VALID_SIDES = {"BUY", "SELL"}
VALID_TIME_IN_FORCE = {"GTC", "IOC", "FOK", "GTX"}
SYMBOL_PATTERN = re.compile(r"^[A-Z0-9]{3,20}$")


def validate_symbol(symbol: str) -> str:
    s = symbol.strip().upper()
    if not SYMBOL_PATTERN.match(s):
        raise ValueError(
            f"Invalid symbol '{symbol}'. Expected alphanumeric uppercase, e.g. BTCUSDT."
        )
    return s


def validate_side(side: str) -> str:
    s = side.strip().upper()
    if s not in VALID_SIDES:
        raise ValueError(f"Invalid side '{side}'. Must be one of: {VALID_SIDES}.")
    return s


def validate_order_type(order_type: str) -> str:
    t = order_type.strip().upper()
    if t not in VALID_ORDER_TYPES:
        raise ValueError(
            f"Invalid order type '{order_type}'. Must be one of: {VALID_ORDER_TYPES}."
        )
    return t


def validate_quantity(quantity: str) -> str:
    try:
        qty = float(quantity)
        if qty <= 0:
            raise ValueError
    except (ValueError, TypeError):
        raise ValueError(f"Invalid quantity '{quantity}'. Must be a positive number.")
    return quantity.strip()


def validate_price(price: str, label: str = "price") -> str:
    try:
        p = float(price)
        if p <= 0:
            raise ValueError
    except (ValueError, TypeError):
        raise ValueError(f"Invalid {label} '{price}'. Must be a positive number.")
    return price.strip()


def validate_time_in_force(tif: str) -> str:
    t = tif.strip().upper()
    if t not in VALID_TIME_IN_FORCE:
        raise ValueError(
            f"Invalid timeInForce '{tif}'. Must be one of: {VALID_TIME_IN_FORCE}."
        )
    return t
