# good-mcp – MCP-Schnittstelle

good-mcp ist ein kleiner Artikeldienst für den MCP-Gate-Selbsttest.

```mcp-meta
{"command": "good-mcp", "cli": "good-cli", "base_url_env": "GOOD_BASE_URL", "secret_env": ["GOOD_TOKEN"], "env": {}}
```

## Tools

```mcp-tools
[{"tool": "search_items", "cli": "good-cli suche", "write": false},
 {"tool": "get_item", "cli": "good-cli zeige", "write": false},
 {"tool": "book_item", "cli": "good-cli buche", "write": true}]
```

## Routen

```mcp-routes
[{"method": "GET", "path": "/items", "query_contains": "q=", "response": "tests/fixtures/mcp/items.json", "status": 200, "content_type": "application/json; charset=utf-8"},
 {"method": "GET", "path": "/item", "query_contains": "id=", "response": "tests/fixtures/mcp/item.json", "status": 200, "content_type": "application/json; charset=utf-8"},
 {"method": "POST", "path": "/book", "response": "tests/fixtures/mcp/book.json", "status": 200, "content_type": "application/json; charset=utf-8"}]
```

## Aufrufe

```mcp-calls
[{"tool": "search_items", "arguments": {"query": "Linsen"}, "expect": ["Linsen"]},
 {"tool": "get_item", "arguments": {"item_id": "1"}, "expect": ["Linsen"]},
 {"tool": "book_item", "arguments": {"item": "1", "confirm": false}, "expect": ["Vorschau"], "expect_no_write": true},
 {"tool": "book_item", "arguments": {"item": "1", "confirm": true}, "expect": ["Buchung bestätigt", "B-1"]}]
```
