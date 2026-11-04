# MCP-Spec: kurstool-mcp

Diese Datei ist die Vorlage für `docs/MCP.md` in jedem MCP-Repo. Sie wird ausgefüllt, sobald die zugehörige CLI UX-Gate und Pflicht-QA bestanden hat. Beispielwerte (Tool `kurstool-mcp`, CLI `kurstool`) werden durch die echten Werte des Projekts ersetzt.

Ablauf beim Ausfüllen:

1. CLI-Befehle auf Tools abbilden; schreibende Tools bekommen `confirm`.
2. Meta, Tools, Routen und Aufrufe als Blöcke eintragen, die `mcp_check.py` parst.
3. Geschäftsmodell notieren.
4. `python tests/harness/mcp_check.py <repo>` laufen lassen; erst bei grünem Gate veröffentlichen.

## Meta

Das Meta-Objekt benennt den Startbefehl, die CLI als Kern-Code und alle Umgebungsvariablen. `base_url_env` zeigt im Test auf den Fake-Server. Secrets stehen nur in `secret_env` und werden nie als Tool-Argument zurückgegeben.

```mcp-meta
{"command": "kurstool-mcp",
 "cli": "kurstool",
 "base_url_env": "KURSTOOL_BASE_URL",
 "secret_env": ["KURSTOOL_LOGIN_USER", "KURSTOOL_LOGIN_PASSWORD"],
 "env": {"KURSTOOL_STATUSGRUPPE": "studierende"}}
```

## Tools

Jedes Tool bildet genau einen CLI-Befehl ab (erstes Wort Programm, zweites Wort Unterkommando) und ruft denselben Kern wie die CLI. `write: true` verlangt den Pflicht-Parameter `confirm: boolean` (ohne `confirm=true` nur Vorschau, kein Request) und entspricht `readOnlyHint=false` oder `destructiveHint=true`. Jedes Tool trägt `annotations` mit `title`, `readOnlyHint`, `destructiveHint`, `openWorldHint`. Für Glamas TDQS (MCP08) gilt zusätzlich: Die Tool-Beschreibung hat mindestens 40 Zeichen, wiederholt nicht nur den Namen und nennt bei mehreren Tools die Verwendung bzw. Abgrenzung („Use when“, „Use this“, „not for“, „Nutze“, „statt“). Jede Property in `inputSchema.properties` bekommt eine nicht-leere `description`; `readOnlyHint` und `destructiveHint` sind immer als bool gesetzt und nie beide `true`.

```mcp-tools
[{"tool": "search_courses", "cli": "kurstool search", "write": false},
 {"tool": "get_course", "cli": "kurstool show", "write": false},
 {"tool": "book_course", "cli": "kurstool book", "write": true}]
```

## Lesende Routen

Format wie `ux-routes` in `docs/UX.md`: `path` wird ohne Querystring exakt verglichen, `query_contains` ist optional. Die Antwortdateien liegen relativ zum Repo.

```mcp-routes
[{"method": "GET", "path": "/kurse", "query_contains": "volleyball", "response": "tests/fixtures/mcp/kurse.html", "status": 200, "content_type": "text/html; charset=utf-8"},
 {"method": "GET", "path": "/kurse/32304", "response": "tests/fixtures/mcp/kurs_32304.html", "status": 200, "content_type": "text/html; charset=utf-8"}]
```

## Aufrufe

Jeder Aufruf nennt Tool und Argumente. `expect` prüft erwartete Textstellen in der Antwort; `expect_no_write: true` prüft, dass ohne `confirm` kein Request am Fake-Server ankommt. Aufrufe mit `expect` laufen über den MCP Inspector; schreibende Aufrufe mit Erwartung geben `confirm` explizit an.

```mcp-calls
[{"tool": "search_courses", "arguments": {"query": "volleyball"}, "expect": ["Volleyball Anfänger", "Kurs 32304"]},
 {"tool": "book_course", "arguments": {"course": "32304", "confirm": false}, "expect": ["Vorschau"], "expect_no_write": true},
 {"tool": "book_course", "arguments": {"course": "32304", "confirm": true}, "expect": ["Buchung bestätigt"]}]
```

## Geschäftsmodell

Eine knappe Notiz je MCP, zum Beispiel:

- Gehostete Variante unter `mcp.human-agent-interface.com/<name>/mcp`.
- Paid Tier für Watch/Alerts.
- B2B für Hochschulen/Praxen.

## Veröffentlichung

README mit `<!-- mcp-name: io.github.smlfg/kurstool-mcp -->` und Config-Snippets für Claude Desktop, Claude Code und Cursor (`mcpServers`-Block). `server.json` für `mcp-publisher`:

```json
{
  "$schema": "https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json",
  "name": "io.github.smlfg/kurstool-mcp",
  "version": "0.1.0",
  "description": "MCP-Server für Kurse und Buchungen",
  "packages": [
    {
      "registryType": "pypi",
      "identifier": "kurstool-mcp",
      "version": "0.1.0",
      "transport": {"type": "stdio"},
      "runtimeHint": "uvx"
    }
  ]
}
```

Die Version in `server.json` ist gleich der Version in `pyproject.toml`. Danach `mcp-publisher validate server.json` (muss Exit 0 liefern), `mcp-publisher publish`, Listing bei Smithery (`smithery.yaml`) und Glama (`glama.json`).
