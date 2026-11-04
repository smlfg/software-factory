# good-mcp

Wohlverhaltener MCP-Selftest-Server für das Gate.

<!-- mcp-name: io.github.smlfg/good-mcp -->

## Claude Desktop / Cursor

```json
{
  "mcpServers": {
    "good-mcp": {
      "command": "uvx",
      "args": ["good-mcp"],
      "env": {"GOOD_BASE_URL": "https://example.invalid"}
    }
  }
}
```

## CLI

```bash
good-cli suche --query Linsen
good-cli zeige --id 1
good-cli buche --item 1 --confirm
```
