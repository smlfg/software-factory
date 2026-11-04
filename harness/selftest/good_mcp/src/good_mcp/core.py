"""CLI-Kern von good-mcp: dieselben Funktionen für CLI und MCP-Tools."""

from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request


def base_url() -> str:
    return os.environ.get("GOOD_BASE_URL", "http://127.0.0.1:9").rstrip("/")


def _request(path: str, data: dict[str, str] | None = None) -> str:
    url = base_url() + path
    try:
        if data is None:
            with urllib.request.urlopen(url, timeout=20) as response:
                return response.read().decode("utf-8", "replace")
        body = urllib.parse.urlencode(data).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=body,
            method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        with urllib.request.urlopen(request, timeout=20) as response:
            return response.read().decode("utf-8", "replace")
    except Exception as exc:  # noqa: BLE001 - MCP-Tool meldet isError ohne Traceback
        raise RuntimeError(f"Netzwerkfehler: {exc}") from exc


def search_items(query: str) -> str:
    return _request("/items?" + urllib.parse.urlencode({"q": query}))


def get_item(item_id: str) -> str:
    return _request("/item?" + urllib.parse.urlencode({"id": item_id}))


def book_item(item: str, confirm: bool) -> str:
    if confirm is not True:
        return f"Vorschau: Buchung von {item} nicht gesendet (confirm=true nötig)"
    body = _request("/book", {"item": item})
    return f"Buchung bestätigt: {body}"


def pretty(text: str) -> str:
    try:
        return json.dumps(json.loads(text), ensure_ascii=False, indent=2)
    except ValueError:
        return text
