"""good-mcp: FastMCP-Server, dessen Tools denselben Kern wie good-cli nutzen."""

from __future__ import annotations

from typing import Annotated

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from . import core

SERVER_NAME = "good-mcp"
mcp = FastMCP(SERVER_NAME)


@mcp.tool(
    name="search_items",
    description="Sucht Artikel im Katalog anhand eines Suchbegriffs.",
    annotations=ToolAnnotations(
        readOnlyHint=True, destructiveHint=False, openWorldHint=True
    ),
)
def search_items(
    query: Annotated[str, Field(description="Suchbegriff für die Artikelsuche")],
) -> str:
    """Sucht Artikel und liefert die Trefferliste als JSON."""
    return core.search_items(query)


@mcp.tool(
    name="get_item",
    description="Liefert die Details eines Artikels anhand seiner ID.",
    annotations=ToolAnnotations(
        readOnlyHint=True, destructiveHint=False, openWorldHint=True
    ),
)
def get_item(
    item_id: Annotated[str, Field(description="Eindeutige Artikel-ID")],
) -> str:
    """Zeigt einen Artikel als JSON."""
    return core.get_item(item_id)


@mcp.tool(
    name="book_item",
    description="Bucht einen Artikel verbindlich nach ausdrücklicher Bestätigung.",
    annotations=ToolAnnotations(
        readOnlyHint=False, destructiveHint=True, openWorldHint=True
    ),
)
def book_item(
    item: Annotated[str, Field(description="ID des zu buchenden Artikels")],
    confirm: Annotated[bool, Field(description="Buchung wirklich senden")],
) -> str:
    """Bucht einen Artikel; ohne confirm=true wird nur eine Vorschau geliefert."""
    return core.book_item(item, confirm)


def main() -> int:
    mcp.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
