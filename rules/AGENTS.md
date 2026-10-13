# Regeln für jedes Modell (aus agent-learnings)

Diese Regeln kommen in den Prompt jedes Bau-Versuchs. Jede Regel verweist auf das Learning, aus dem sie stammt.

## Sicherheit (immer)
- Passwörter, TOTP-Codes und TOTP-Secrets werden nie gespeichert, geloggt, als CLI-Flag angenommen oder an ein LLM gegeben. Eingabe nur über verdeckten Prompt.
- Sessions liegen im OS-Schlüsselbund, sonst in einer Datei mit Rechten 0600, nie im Repo oder Arbeitsverzeichnis, nie in Ausgaben oder MCP-Antworten.
- Nur die Cookies der Ziel-App speichern (Allowlist), nie Cookies des Identity-Providers. → `learnings/2026-10-08-nur-noetige-cookies-speichern.md`
- Keine persönlichen Daten erfinden (Mail, Telefon, Adresse, Matrikelnummer). Autor in `pyproject.toml`/`package.json` nur als Name plus `186922365+smlfg@users.noreply.github.com`, sonst Feld weglassen. → `learnings/2026-10-08-keine-erfundenen-personendaten.md`

## Auth
- Login gilt erst als erfolgreich, wenn eine nur für eingeloggte Nutzer sichtbare Seite geladen wurde, nie schon, wenn ein Cookie existiert. → `learnings/2026-10-08-login-erfolg-braucht-beweis.md`
- Abgelaufene Session erkennen und klar melden, kein automatischer Re-Login.

## Fehler und Exit-Codes
- Erst HTTP-Status prüfen, dann parsen. Jede Fehlerklasse hat genau einen Exit-Code bzw. MCP-Fehlertyp, „unbekannt“ ist nie „Erfolg“. → `learnings/2026-10-08-fehlerklassen-auf-exitcodes.md`
- Auch Usage-/Subparser-Fehler liefern mit `--json` genau ein JSON-Objekt (Parser zentral abfangen). → `learnings/2026-10-13-wifionice-cli-LEARNINGS.md`
- Env-/Config-Werte robust validieren: unparsebare Zahlen, NaN/Inf, ungültige URLs → sauberer Fehler ohne Traceback. → `learnings/2026-10-13-wifionice-cli-LEARNINGS.md`
- Schreibende Aktionen prüfen `--confirm`/`--dry-run` VOR jedem Request; `--dry-run` sendet nie — auch keine Zugangsdaten. → `learnings/2026-10-13-hochschulstart-cli-LEARNINGS.md`

## Schnittstelle
- INTERFACE.md wörtlich umsetzen: Flags, Exit-Codes, Ausgabeformat. Keine eigenen Abweichungen. → `learnings/2026-10-08-schnittstellenvertrag-woertlich.md`
- Aufräum-Befehle (logout, delete, …) sind idempotent.
- Mit `--json` steht auf stdout genau ein JSON-Objekt, Prompts gehen auf stderr.

## Tests
- Das Tool darf in Tests nie echte Server erreichen. Konfigurationspfade aus Umgebungsvariablen respektieren. → `learnings/2026-10-08-netzwerk-sandbox-in-tests.md`

## Scraping / HTML-Parsing
- Listen-Parser über stabile Klassen/Selektoren (z. B. `h2.truncate_title`), nie „erstes <span>/<div>“. Detail-URLs oft mit numerischer ID ausreichend, wenn der Server redirected. Mehrere Feld-Schemata auf Detailseiten explizit abdecken. → `learnings/2026-10-13-wg-gesucht-cli-LEARNINGS.md`
- HTML-Entities: `convert_charrefs=False` nur zusammen mit `handle_entityref`/`handle_charrefs` — sonst verschwinden Umlaute (`f&uuml;r` → `fr`). → `learnings/2026-10-13-hochschulstart-cli-LEARNINGS.md`

## Prozess
- Nach jedem Bau eine QA-Runde als eigene Iteration (find→file, nie fixen); auch bei grüner Suite fanden beide Runden echte Betriebsbugs (3+5). → `learnings/2026-10-13-cli-fabrik-LEARNINGS.md`
- Pro CLI ein Repo, kleinteilige Commits, Issues als Loop-Backlog (Dedupe inkl. geschlossener). → `learnings/2026-10-13-cli-fabrik-LEARNINGS.md`
