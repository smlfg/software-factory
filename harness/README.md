# Projektunabhängige Test-Bausteine

## harness/
Aus smlfg/ilias-cli übernommen, enthält nichts ILIAS-Spezifisches:
- `sitecustomize.py`: Netzwerk-Sandbox. Über `PYTHONPATH` in den Subprozess des Tools laden, dann sind nur Verbindungen zu localhost erlaubt und jeder andere Versuch wird protokolliert.
- `leak_check.py`: Sucht ein Geheimnis (roh, URL- und Base64-kodiert) in Ausgaben und Dateibäumen.

## Später
Contract-Tests, die aus Learnings mit `status: offen` entstehen (z. B. „Login-Erfolg braucht Beweis“ als generischer Test gegen einen Fake-Server).

## UX-Gate

`ux_check.py` prüft ein Repo gegen die UX-Spezifikation in `docs/UX.md`
(Format: `scratch/FORMAT.md`). Es nutzt `ux_spec.py`, `fake_server.py` und
`ux_session.py`; nur Standardbibliothek.

```bash
python tests/harness/ux_check.py <repo_dir> [--venv DIR] [--report FILE]
python tests/harness/ux_check.py <repo_dir> --spec-only
python tests/harness/ux_check.py tests/harness/selftest/good_cli --venv scratch/tmp/ux-venv
pytest -q tests/harness
```

- `UX00`: Mit `ux-routes`/`ux-formsteps` muss während der Sitzungen mindestens ein Request am Fake-Server ankommen (und keiner an einen fremden Host gehen), sonst wirkt `base_url_env` nicht.
- `UX01`: `docs/UX.md` fehlt/ungültig, kein `ux-meta`, weniger als drei `ux-session` oder schreibende Sitzung und `ux-formsteps` passen nicht zusammen.
- `UX02`: Credential-Env-Variablen im Quellcode oder in `meta.credential_env`, aber `<tool> --help` kennt kein Unterkommando `login`.
- `UX03`: `<tool> --help`, `<tool> --version` und `<tool> <sub> --help` für alle gefundenen Unterkommandos enden mit Exit 0.
- `UX04`: Keine Pflicht-Option (`--x WERT` außerhalb `[...]`, bei click `[required]`) in der Subkommando-Usage, außer sie steht in `meta.required_options_ok`.
- `UX05`: Kein JSON am Terminalanfang und kein Traceback in den pty-Sitzungen; zusätzlich `login` + Strg+D ohne Traceback.
- `UX06`: README-Schnellstart (Überschrift in den ersten 40 Zeilen) ohne `#`/`$ `-Zeilen und Platzhalter, mit passender Installationszeile und allen Tool-Befehlen als `$ `-Zeile in einer `ux-session`.
- `UX07`: Schreibende Aktionen fragen im TTY nach `[j/N]`; kein formstep ohne `before_confirm` vor der Bestätigung.
- `UX08`: Alle `ux-formsteps` werden mit allen `sends`-Feldern in Reihenfolge gesendet (nutzt dieselbe Logik wie `ux_session.py`).
- `UX09`: Voraussetzungen vor der Bestätigung. (a) In frischem HOME/XDG ohne vorherige Login-Sitzung und ohne `credential_env` darf die schreibende Aktion weder `[j/N]` ausgeben noch formsteps ohne `before_confirm` senden; sie muss auf `<tool> login` verweisen und mit Exit ≠ 0 enden. (b) Im regulären j-Lauf (Login zuerst) müssen alle Felder aus dem Formular des vorherigen formsteps wieder gesendet werden; mit `required` markierte Felder dürfen nicht leer sein.

Exit-Codes: `0` = kein FAIL (SKIP erlaubt), `1` = mindestens ein FAIL,
`2` = Aufruffehler. `--spec-only` prüft nur `UX01` sowie die statischen Teile
von `UX06` und `UX07` und installiert nichts.

In ein neues Repo kopiert man `tests/harness/` komplett (inklusive
`ux_spec.py`, `fake_server.py`, `ux_session.py`, `ux_check.py`,
`sitecustomize.py` und `selftest/`) und ruft `ux_check.py` dort mit
`docs/UX.md` als Eingabe auf.

## MCP-Gate

`mcp_check.py` prüft MCP-Server über stdio gegen `docs/MCP.md` (Blöcke
`mcp-meta`, `mcp-tools`, `mcp-routes`, `mcp-calls`). `MCP01` (tools/list) und
`MCP03` (Aufrufe) laufen über den offiziellen MCP Inspector im CLI-Modus
(`npx -y @modelcontextprotocol/inspector@latest --cli … --method …`), weil er
ein geprüfter Referenz-Client mit JSON-Ausgabe und Exit-Codes ist. Fehlen `npx`
oder Node >= 22.19, fällt das Gate auf `mcp_client.py` zurück und vermerkt
„Inspector fehlt, Fallback“ im Detail (kein FAIL). `MCP00` (stray stdout) und
`MCP04` (unbekanntes Tool, falsche Typen, unerreichbare URL) bleiben beim rohen
JSON-RPC-Client, weil der Inspector diese Protokolldetails nicht roh liefert.
Routen laufen über denselben `fake_server.py` wie das UX-Gate.

```bash
python harness/mcp_check.py <repo_dir> [--venv DIR] [--report FILE] [--cmd "befehl args"]
python harness/mcp_check.py harness/selftest/good_mcp --venv scratch/tmp/mcp-venv
```

- `MCP00`: Start/initialize, `serverInfo`, `capabilities.tools`, kein stray stdout.
- `MCP01`: `tools/list` über den Inspector: Namen, Beschreibungen, Schemata,
  `readOnlyHint`.
- `MCP02`: Schreibende Tools (`readOnlyHint=false` oder `destructiveHint=true`)
  brauchen eine boolean-Property `confirm` in `required`. Jeder Aufruf mit
  `expect_no_write` wird mit `confirm=false` wiederholt und darf am Fake-Server
  kein `POST`/`PUT`/`PATCH`/`DELETE` auslösen (`server.mark()` vor dem Aufruf).
- `MCP03`: Alle `mcp-calls` mit `expect` laufen über den Inspector: kein
  `isError`, alle erwarteten Texte enthalten, mindestens ein Request am
  Fake-Server, kein fremder Host im Sandbox-Protokoll (`sitecustomize.py`).
- `MCP04`: Fehlerpfade für unbekannte Tools, falsche Typen und unerreichbare URL.
- `MCP05`: Keine Secrets in stdout/stderr/Antworten.
- `MCP06`: `server.json` existiert und ist gültig, `name` beginnt mit
  `io.github.smlfg/`, Version und Paket-Identifier passen zu `pyproject.toml`,
  README enthält den `mcp-name`-Kommentar und einen `mcpServers`-Block. Ist
  `mcp-publisher` installiert, muss `mcp-publisher validate server.json` mit
  Exit 0 enden; sonst SKIP-Hinweis.
- `MCP07`: `mcp-tools` nennt Tool, CLI-Befehl und `write`-Flag. Jedes Tool
  existiert in `tools/list`, Programm und Unterkommando stehen in
  `<programm> --help` aus dem venv, `write=true` entspricht genau dem
  `confirm`-Schema aus `MCP02`.
- `MCP08`: Tool-Definitionsqualität nach Glamas TDQS. Jede Beschreibung hat
  mindestens 40 Zeichen und wiederholt nicht nur den Namen; bei mehr als einem
  Tool nennt sie die Verwendung bzw. Abgrenzung („Use when“, „Use this“,
  „prefer“, „not for“, „vs“, „Nutze“, „statt“). Jede Property in
  `inputSchema.properties` braucht eine nicht-leere `description`
  (Abdeckung 100 %). Jedes Tool setzt `readOnlyHint` und `destructiveHint` als
  bool; beide gleichzeitig `true` ist ein Fehler. Ist `uvx` im PATH, läuft
  zusätzlich `uvx tdqs lint --file <tools.json> --fail-on error --format json`
  (Exit 1 = FAIL, Exit 2 oder fehlendes `uvx` = Hinweis, kein FAIL).

Exit-Codes wie beim UX-Gate: `0` = kein FAIL (SKIP erlaubt), `1` = FAIL,
`2` = Aufruffehler.
