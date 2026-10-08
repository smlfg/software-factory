# Regeln für jedes Modell (aus agent-learnings)

Diese Regeln kommen in den Prompt jedes Bau-Versuchs. Jede Regel verweist auf das Learning, aus dem sie stammt.

## Sicherheit (immer)
- Passwörter, TOTP-Codes und TOTP-Secrets werden nie gespeichert, geloggt, als CLI-Flag angenommen oder an ein LLM gegeben. Eingabe nur über verdeckten Prompt.
- Sessions liegen im OS-Schlüsselbund, sonst in einer Datei mit Rechten 0600, nie im Repo oder Arbeitsverzeichnis, nie in Ausgaben oder MCP-Antworten.
- Nur die Cookies der Ziel-App speichern (Allowlist), nie Cookies des Identity-Providers. → `learnings/2026-10-08-nur-noetige-cookies-speichern.md`

## Auth
- Login gilt erst als erfolgreich, wenn eine nur für eingeloggte Nutzer sichtbare Seite geladen wurde, nie schon, wenn ein Cookie existiert. → `learnings/2026-10-08-login-erfolg-braucht-beweis.md`
- Abgelaufene Session erkennen und klar melden, kein automatischer Re-Login.

## Fehler und Exit-Codes
- Erst HTTP-Status prüfen, dann parsen. Jede Fehlerklasse hat genau einen Exit-Code bzw. MCP-Fehlertyp, „unbekannt“ ist nie „Erfolg“. → `learnings/2026-10-08-fehlerklassen-auf-exitcodes.md`

## Schnittstelle
- INTERFACE.md wörtlich umsetzen: Flags, Exit-Codes, Ausgabeformat. Keine eigenen Abweichungen. → `learnings/2026-10-08-schnittstellenvertrag-woertlich.md`
- Aufräum-Befehle (logout, delete, …) sind idempotent.
- Mit `--json` steht auf stdout genau ein JSON-Objekt, Prompts gehen auf stderr.

## Tests
- Das Tool darf in Tests nie echte Server erreichen. Konfigurationspfade aus Umgebungsvariablen respektieren. → `learnings/2026-10-08-netzwerk-sandbox-in-tests.md`
