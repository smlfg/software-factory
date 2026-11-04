"""Kleine CLI (good-cli) für den MCP-Gate-Selbsttest."""

from __future__ import annotations

import argparse
import sys

from . import core


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="good-cli",
        description="Artikeldienst für den MCP-Gate-Selbsttest.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    suche = sub.add_parser("suche", help="Artikel im Katalog suchen")
    suche.add_argument("--query", required=True, help="Suchbegriff")

    zeige = sub.add_parser("zeige", help="Artikeldetails anzeigen")
    zeige.add_argument("--id", required=True, help="Artikel-ID")

    buche = sub.add_parser("buche", help="Artikel verbindlich buchen")
    buche.add_argument("--item", required=True, help="Artikel-ID")
    buche.add_argument(
        "--confirm",
        action="store_true",
        help="Buchung wirklich senden",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "suche":
            print(core.pretty(core.search_items(args.query)))
        elif args.command == "zeige":
            print(core.pretty(core.get_item(args.id)))
        elif args.command == "buche":
            print(core.book_item(args.item, args.confirm))
    except RuntimeError as exc:
        print(f"Fehler: {exc}", file=sys.stderr)
        return 1
    return 0
