#!/usr/bin/env python3
"""
Binance Futures Testnet CLI Trading Bot
Usage examples:
  python cli.py market --symbol BTCUSDT --side BUY --quantity 0.001
  python cli.py limit  --symbol BTCUSDT --side SELL --quantity 0.001 --price 70000
  python cli.py stop   --symbol BTCUSDT --side SELL --quantity 0.001 --price 69000 --stop-price 69500
"""

import argparse
import os
import sys

from dotenv import load_dotenv

from bot.logging_config import configure_logging, get_logger
from bot.orders import place_order, print_order_response, print_order_summary
from bot.client import BinanceClient

# Bootstrap logging before anything else
configure_logging()
logger = get_logger(__name__)


def load_credentials() -> tuple[str, str]:
    """Load API credentials from .env file or environment variables."""
    load_dotenv()
    api_key = os.getenv("BINANCE_API_KEY", "").strip()
    api_secret = os.getenv("BINANCE_API_SECRET", "").strip()
    if not api_key or not api_secret:
        logger.error(
            "BINANCE_API_KEY and BINANCE_API_SECRET must be set in .env or environment."
        )
        sys.exit(1)
    return api_key, api_secret


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Binance Futures Testnet CLI Trading Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    subparsers = parser.add_subparsers(dest="command", required=True, help="Order type")

    # ── Shared parent parser ─────────────────────────────────────────────────
    shared = argparse.ArgumentParser(add_help=False)
    shared.add_argument(
        "--symbol", required=True, help="Trading pair symbol, e.g. BTCUSDT"
    )
    shared.add_argument(
        "--side", required=True, choices=["BUY", "SELL", "buy", "sell"], help="Order side"
    )
    shared.add_argument("--quantity", required=True, help="Order quantity")

    # ── MARKET ───────────────────────────────────────────────────────────────
    subparsers.add_parser(
        "market",
        parents=[shared],
        help="Place a MARKET order",
        description="Place a MARKET order. No price required.",
    )

    # ── LIMIT ────────────────────────────────────────────────────────────────
    limit_parser = subparsers.add_parser(
        "limit",
        parents=[shared],
        help="Place a LIMIT order",
        description="Place a LIMIT order.",
    )
    limit_parser.add_argument("--price", required=True, help="Limit price")
    limit_parser.add_argument(
        "--time-in-force",
        dest="time_in_force",
        default="GTC",
        choices=["GTC", "IOC", "FOK", "GTX"],
        help="Time in force (default: GTC)",
    )

    # ── STOP-LIMIT (bonus) ───────────────────────────────────────────────────
    stop_parser = subparsers.add_parser(
        "stop",
        parents=[shared],
        help="Place a STOP-LIMIT order (bonus)",
        description="Place a STOP-LIMIT order. Requires both --price and --stop-price.",
    )
    stop_parser.add_argument("--price", required=True, help="Limit price (triggered price)")
    stop_parser.add_argument(
        "--stop-price",
        dest="stop_price",
        required=True,
        help="Stop trigger price",
    )
    stop_parser.add_argument(
        "--time-in-force",
        dest="time_in_force",
        default="GTC",
        choices=["GTC", "IOC", "FOK", "GTX"],
        help="Time in force (default: GTC)",
    )

    return parser


def run(args: argparse.Namespace) -> None:
    """Core execution: validate → summarise → place → display."""
    order_type_map = {"market": "MARKET", "limit": "LIMIT", "stop": "STOP"}
    args.type = order_type_map[args.command]

    # Normalise optional attributes so print_order_summary is safe
    if not hasattr(args, "price"):
        args.price = None
    if not hasattr(args, "stop_price"):
        args.stop_price = None
    if not hasattr(args, "time_in_force"):
        args.time_in_force = None

    print_order_summary(args)

    api_key, api_secret = load_credentials()
    client = BinanceClient(api_key, api_secret)

    try:
        response = place_order(
            client=client,
            symbol=args.symbol,
            side=args.side,
            order_type=args.type,
            quantity=args.quantity,
            price=args.price,
            stop_price=args.stop_price,
            time_in_force=args.time_in_force,
        )
        print_order_response(response)
    except ValueError as exc:
        logger.error("Validation error: %s", exc)
        print(f"\n[ERROR] {exc}\n")
        sys.exit(2)
    except RuntimeError as exc:
        logger.error("Order failed: %s", exc)
        print(f"\n[ERROR] {exc}\n")
        sys.exit(3)


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
