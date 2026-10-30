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

## Bedienbarkeit für Menschen (Pflicht)
- Jede CLI muss für Menschen bedienbar sein: `login`-Kommando statt nur Env, Namen statt IDs, interaktive Bestätigung im TTY, `--confirm` nur für Agenten, README-Schnellstart. → `learnings/2026-10-30-cli-fuer-menschen-bedienbar.md`
  - `login` fragt im Terminal interaktiv (Passwort per getpass), speichert in Schlüsselbund oder Config-Datei 0600; dazu `logout` und `whoami`/`status` ohne Passwort-Ausgabe. Env-Variablen überschreiben die Config und bleiben für Agenten.
  - Suchen und Aktionen nehmen Namen/Freitext positional (`tool book volleyball`, `tool search fahrrad`); bei mehreren Treffern nummerierte Auswahl im TTY, ohne TTY Liste + Exit Usage.
  - Schreibende Aktionen fragen im TTY „… verbindlich? [j/N]“ (Default Nein); `--confirm`/`--yes` nur für nicht-interaktive Agenten; ohne TTY und ohne Flag Trockenlauf bzw. Abbruch vor jedem Request.
  - Ausgabe im Terminal lesbar, JSON nur mit `--json` oder wenn stdout kein Terminal ist (Pipe/Agent).
  - Fehler nennen den nächsten Schritt („Login fehlt – `tool login` ausführen“), nie Tracebacks bei EOF/Strg+C/fehlender optionaler Abhängigkeit.
  - README beginnt mit „Schnellstart“: `pipx install git+https://github.com/smlfg/<repo>` (landet im PATH), Login, ein typischer Befehl mit Namen.

## Tests
- Das Tool darf in Tests nie echte Server erreichen. Konfigurationspfade aus Umgebungsvariablen respektieren. → `learnings/2026-10-08-netzwerk-sandbox-in-tests.md`

## Scraping / HTML-Parsing
- Listen-Parser über stabile Klassen/Selektoren (z. B. `h2.truncate_title`), nie „erstes <span>/<div>“. Detail-URLs oft mit numerischer ID ausreichend, wenn der Server redirected. Mehrere Feld-Schemata auf Detailseiten explizit abdecken. → `learnings/2026-10-13-wg-gesucht-cli-LEARNINGS.md`
- HTML-Entities: `convert_charrefs=False` nur zusammen mit `handle_entityref`/`handle_charrefs` — sonst verschwinden Umlaute (`f&uuml;r` → `fr`). → `learnings/2026-10-13-hochschulstart-cli-LEARNINGS.md`

## Prozess
- Nach jedem Bau eine QA-Runde als eigene Iteration (find→file, nie fixen); auch bei grüner Suite fanden beide Runden echte Betriebsbugs (3+5). → `learnings/2026-10-13-cli-fabrik-LEARNINGS.md`
- Pro CLI ein Repo, kleinteilige Commits, Issues als Loop-Backlog (Dedupe inkl. geschlossener). → `learnings/2026-10-13-cli-fabrik-LEARNINGS.md`

- Jeder Filter (auch `--date`) wird clientseitig gegen jeden Treffer erzwungen; die API kann mehr liefern als angefragt (z.B. Nachtfahrten des Folgetags). QA prüft Filter über die komplette Trefferliste. (2026-10-21, flixbus-cli)
- Pflicht-QA enthält immer den Prüfpunkt „Bedienbarkeit für Menschen“: frisch per `pipx install git+…` installieren und Befehl im PATH aufrufen; Haupt-Use-Case ohne README nur mit `--help` im Terminal (pseudo-TTY, z. B. `script -qc`) durchspielen: `login` interaktiv, Suche per Name, Bestätigungsfrage mit Antwort „N“ sendet nichts; Fehler ohne Login nennen den nächsten Schritt. FAIL, wenn eine Kernaktion nur über Env/IDs/`--confirm` erreichbar ist. (2026-10-30, hochschulsport-cli)
