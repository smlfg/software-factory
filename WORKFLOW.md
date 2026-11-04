# Workflow: Website rein, CLI raus

Bausteine: Startgerüst [smlfg/cli-mcp-template](https://github.com/smlfg/cli-mcp-template) (enthält `docs/UX.md`-Vorlage und `tests/harness/` mit UX-Gate), Regeln [rules/AGENTS.md](rules/AGENTS.md), Gate-Doku [tests/README.md](tests/README.md), UX-Vorlage [template/UX.md](template/UX.md).

Ein durchgehender Ablauf von oben nach unten. Jeder Schritt hat eine Eingabe, eine Ausgabe und ein Gate. Kein Schritt wird übersprungen; ein rotes Gate schickt zurück, nicht weiter.

```
Thema (topics/, NEXT20.md)
        |
        v
[0] Thema wählen
        |
        v
[1] Demand-Gate (Smithery/Glama/mcp.so, GitHub, Reddit)
        |  keine belegte Nachfrage -> zurück zu [0]
        v
[2] Live-Erkundung + docs/UX.md
        |  Gate: ux_check.py --spec-only / UX01 grün
        v
[3] ANFORDERUNGEN.md + INTERFACE.md + README-Schnellstart
        |      + Akzeptanztests aus docs/UX.md
        v
[4] Bau in kleinen Schritten (opencode)
        |  je Schritt: Commit + pytest
        v
[5] UX-Gate: ux_check.py (UX01-UX08) + ux_session.py
        |  FAIL -> zurück zu [4], nicht weiter
        v
[6] Pflicht-QA (find -> file: pipx, live lesend, Filter, Terminal)
        |
        v
[7] Push + About/Topics + Meldung an Samuel + LOG.md + runs/runs.csv
        |
        v
[M1] MCP-Zuschnitt: eigenes Repo <name>-mcp, CLI als Abhängigkeit
        |  Gate: mcp-tools (Tool -> CLI-Befehl) + annotations
        v
[M2] docs/MCP.md nach template/MCP.md
        |  Gate: template-Blöcke vorhanden und parsebar
        v
[M3] MCP-Gate: mcp_check.py (MCP00-MCP07) + QA-Smoke
        |  FAIL -> zurück zu [M1], nicht weiter
        v
[M4] Veröffentlichen: PyPI (uvx), mcp-publisher, Smithery/Glama
```

## Schritt 0: Thema wählen

| Feld | Inhalt |
|---|---|
| Eingabe | `topics/` (Backlog), `NEXT20.md` der Routine, offene Issues |
| Ausgabe (Dateien) | Themenzeile mit Repo-Name und Typ (`cli` oder `mcp`) |
| Gate | Thema hat einen konkreten Nutzer-Nutzen, eine erreichbare Schnittstelle und kein bestehendes Tool mit gleicher Abdeckung |
| Worker | Samuel (Auswahl), opencode (Vorabprüfung der Schnittstelle) |

## Schritt 1: Demand-Gate

| Feld | Inhalt |
|---|---|
| Eingabe | Thema aus Schritt 0 |
| Ausgabe (Dateien) | Abschnitt `Nachfrage` in `ANFORDERUNGEN.md` mit Quellen und Datum |
| Gate | Nachfrage belegt durch Smithery/Glama/mcp.so-Eintrag, GitHub-Requests/Issues oder Reddit-Threads. Ohne Beleg kein Bau. |
| Worker | opencode (Recherche), Grok Bot (nur Bericht lesen) |

Erfolg wird später nur über GitHub-Traffic und Smithery-Calls gemessen, nie über PyPI-Downloads.

## Schritt 2: Live-Erkundung und UX-Spec

| Feld | Inhalt |
|---|---|
| Eingabe | echte Website, Konto/Testzugang, Thema |
| Ausgabe (Dateien) | `docs/UX.md` nach `template/UX.md`, `tests/fixtures/ux/*` |
| Gate | `python tests/harness/ux_check.py --spec-only` bzw. UX01 grün: Spec parst, Meta vorhanden, mindestens 3 Sitzungen, schreibende Aktion und Formsteps passen zusammen |
| Worker | opencode (Erkundung), Samuel (nur Zugang/Freigabe) |

Vor jeder Codezeile entstehen die drei wichtigsten Nutzer-Aufgaben als exakt abtippbare Terminal-Sitzungen:

1. Installation per `pipx` und `<tool> login` interaktiv (eine Sitzung).
2. Suche per Name.
3. Schreibende Aktion bis zum letzten Schritt inklusive `[j/N]`.

Alle Formular- und Request-Schritte der schreibenden Aktion werden live erkundet, lesend. Nur Schritte, die nichts verbindlich auslösen, dürfen live gesendet werden. Alles danach wird synthetisch nachgebaut und in `ux-formsteps` als `"live": "synthetisch"` markiert. Zu jeder Sitzung gehören Fixtures unter `tests/fixtures/ux/`.

## Schritt 3: Requirements und Akzeptanztests

| Feld | Inhalt |
|---|---|
| Eingabe | `docs/UX.md`, Ergebnisse der Live-Erkundung |
| Ausgabe (Dateien) | `ANFORDERUNGEN.md`, `INTERFACE.md`, `README.md` (Schnellstart), `tests/acceptance/` |
| Gate | Jede UX-Sitzung hat mindestens einen Akzeptanztest; der README-Schnellstart ist wörtlich aus den UX-Sitzungen übernommen (Befehle identisch); `INTERFACE.md` nennt Flags, Exit-Codes und Ausgabeformat |
| Worker | opencode |

## Schritt 4: Bau in kleinen Schritten

| Feld | Inhalt |
|---|---|
| Eingabe | `ANFORDERUNGEN.md`, `INTERFACE.md`, `docs/UX.md`, `rules/AGENTS.md`, `tests/` |
| Ausgabe (Dateien) | Quellcode, `tests/acceptance/`-Läufe, je Schritt ein Commit |
| Gate | Nach jedem Schritt `pytest` grün und ein eigener Commit; keine offenen Tracebacks |
| Worker | opencode Go `opencode-go/deepseek-v4.1-flash` (bezahlt), bei Limit/429 Fallback auf `deepseek-v4.1-flash-free` → `glm-5.3-flash-free` → `mimo-v2.6-flash-free`; gestartet über `/home/box/scripts/hermes-run.sh` mit Shim, der den Go-Key nur für `opencode-go/*` setzt |

## Schritt 5: UX-Gate

| Feld | Inhalt |
|---|---|
| Eingabe | fertiger Build, `docs/UX.md`, Fixtures |
| Ausgabe (Dateien) | Markdown-Bericht von `ux_check.py` und `ux_session.py` |
| Gate | `python tests/harness/ux_check.py <repo>`: UX00-UX08 ohne FAIL (UX00 = Tool über `base_url_env` gegen den Fake-Server testbar). `python tests/harness/ux_session.py <repo>`: frisches venv, Befehl im PATH, Login-Prompts, Auswahl per Name, `N` bricht ohne Request ab, `j` gegen Fake-Server sendet ALLE Formularschritte. Kein PASS -> zurück zu Schritt 4. |
| Worker | opencode (Ausführung), Grok Bot (nur Bericht lesen) |

## Schritt 6: Pflicht-QA

| Feld | Inhalt |
|---|---|
| Eingabe | Build aus Schritt 5, echte Website, Testkonto |
| Ausgabe (Dateien) | `docs/QA.md` mit Befund je Prüfung, Issues für offene Punkte |
| Gate | Eigene Iteration nach find -> file (nicht fixen): frische `pipx`-Installation, Live-Aufrufe nur lesend, semantische Checks (jeder Filter über alle Treffer), Bedienbarkeit im echten Terminal. Jeder FAIL ist als Issue oder Fix belegt. |
| Worker | opencode (Durchführung), Samuel (Gegenprobe am Terminal) |

## Schritt 7: Veröffentlichen und melden

| Feld | Inhalt |
|---|---|
| Eingabe | Build und QA aus Schritt 5 und 6 |
| Ausgabe (Dateien) | öffentliches Repo mit About/Topics, Meldung an Samuel, `LOG.md`, Zeile in `runs/runs.csv` |
| Gate | Repo public, About und Topics gesetzt; Meldung enthält was gebaut wurde, Schnellstart und offene Punkte; `LOG.md` und `runs.csv` aktualisiert |
| Worker | tägliche Routine (Grok Bot orchestriert: Push, Meldung), opencode (Texte, LOG-/runs-Einträge) |

## MCP-Strang (Schritte M1-M4)

Jede CLI, die UX-Gate (Schritt 5) und Pflicht-QA (Schritt 6) bestanden hat, bekommt einen MCP-Server. Der Strang läuft nach Schritt 7 und nutzt denselben Kern-Code; die Schritte 0-7 bleiben unverändert.

## Schritt M1: Zuschnitt

| Feld | Inhalt |
|---|---|
| Eingabe | grüne CLI aus Schritt 5 und 6, `INTERFACE.md`, `docs/UX.md` |
| Ausgabe (Dateien) | eigenes Repo `smlfg/<name>-mcp`, `docs/MCP.md` mit Block `mcp-tools` (Tabelle Tool -> CLI-Befehl) |
| Gate | Das Repo nutzt das CLI-Paket als Abhängigkeit (gleicher Kern-Code, keine Kopie der Logik). Jedes Tool bildet einen CLI-Befehl ab. Schreibende Tools haben den Pflicht-Parameter `confirm: boolean`; ohne `confirm=true` gibt es kein Request, nur eine Vorschau. Jedes Tool trägt `annotations` mit `title`, `readOnlyHint`, `destructiveHint`, `openWorldHint`. Secrets nur über Env oder die 0600-Login-Config der CLI, nie als Tool-Argument zurückgegeben. |
| Worker | opencode Go (`opencode-go/deepseek-v4.1-flash`), Fallback Gratis (`deepseek-v4.1-flash-free` → `glm-5.3-flash-free` → `mimo-v2.6-flash-free`) |

## Schritt M2: MCP-Doku

| Feld | Inhalt |
|---|---|
| Eingabe | CLI-Repo, `template/MCP.md` |
| Ausgabe (Dateien) | `docs/MCP.md` mit `mcp-meta` (command, cli, base_url_env, secret_env, env), `mcp-routes` (Format wie `ux-routes`), `mcp-calls` (tool, arguments, expect bzw. expect_no_write) |
| Gate | Alle Blöcke nach `template/MCP.md` vorhanden und parsebar |
| Worker | opencode |

## Schritt M3: MCP-Gate

| Feld | Inhalt |
|---|---|
| Eingabe | MCP-Repo, `docs/MCP.md`, Fake-Server |
| Ausgabe (Dateien) | Bericht von `mcp_check.py`, `docs/QA.md` Abschnitt `MCP` |
| Gate | `python tests/harness/mcp_check.py <repo>` ohne FAIL: MCP00 Start über stdio + `initialize`, kein Fremd-Output auf stdout; MCP01 `tools/list` gültig (Namen, description >= 20 Zeichen, inputSchema object, Property-Beschreibungen, annotations); MCP02 schreibende Tools: `confirm` Pflicht, ohne `confirm` kein Schreib-Request am Fake-Server; MCP03 alle `mcp-calls` gegen den Fake-Server liefern erwartete Texte, mindestens ein Request kommt am Fake-Server an, keiner an fremde Hosts; MCP04 Fehlerpfade (unbekanntes Tool, falsche Typen, Dienst nicht erreichbar) liefern MCP-Fehler bzw. `isError` statt Traceback, Server läuft weiter; MCP05 keine Secrets (Kanarienwerte) in Ausgaben; MCP06 Publish-Metadaten: `server.json` (Name `io.github.smlfg/<name>-mcp`, Version = pyproject), README mit `<!-- mcp-name: ... -->` und Config-Snippets für Claude Desktop/Claude Code/Cursor; MCP07 jedes Tool aus `mcp-tools` existiert in `tools/list` und der zugeordnete CLI-Befehl in `<cli> --help`. Danach QA-Smoke mit echtem MCP-Client (offizielles Python-SDK `mcp` oder `npx @modelcontextprotocol/inspector --cli`; Inspector braucht Node >= 22.19): `tools/list` + jedes lesende Tool einmal live, Ergebnis in `docs/QA.md` Abschnitt `MCP`. |
| Worker | opencode (Ausführung), Samuel (Gegenprobe) |

## Schritt M4: Veröffentlichen

| Feld | Inhalt |
|---|---|
| Eingabe | grüner MCP-Gate, `server.json`, README |
| Ausgabe (Dateien) | PyPI-Paket, `server.json` veröffentlicht, Listing Smithery (`smithery.yaml`) und Glama (`glama.json`), README-Abschnitt „In Claude/Cursor nutzen“, Geschäftsmodell-Notiz in `docs/MCP.md` |
| Gate | Push nur bei grünem Gate; `mcp-publisher validate server.json` und `mcp-publisher publish` grün; PyPI-Paket nur mit vorhandenem Token und `uvx`-fähig; Remote-Variante (Streamable HTTP, gehostet) prüfen und für öffentliche, login-freie Dienste bevorzugen. |
| Worker | tägliche Routine (Push, Meldung), opencode (Metadaten, Texte) |

Erfolg wird nur über GitHub-Traffic (`gh api repos/smlfg/<repo>/traffic/views|clones|popular/referrers`, 14 Tage, regelmäßig sichern) und Smithery-Tool-Calls gemessen, nie über PyPI-Downloads.

Je MCP steht eine Geschäftsmodell-Notiz in `docs/MCP.md` (z. B. gehostete Version, Paid Tier für Watch/Alerts, B2B für Hochschulen/Praxen); die Rangliste steht in `/home/box/cli-daily/MCP-NEXT.md`.

### Lehren aus chefkoch-mcp (04.11.2026, erster Server durch den Strang)

- PyPI lehnt Git-Abhängigkeiten ab: Erst die CLI auf PyPI veröffentlichen (`license = "MIT"` als SPDX, ohne License-Classifier, `twine check`), dann den MCP-Server mit `<cli>>=x.y.z`. Für den Gate-Lauf vor dem Release das CLI-Wheel lokal bauen und `PIP_FIND_LINKS=scratch/wheels` setzen.
- Der Inspector schickt `--tool-arg` als JSON: rein numerische IDs kommen als Zahl. ID-Parameter immer `str | int`.
- Fehlermeldungen im MCP nennen Tools (`search_recipes`), nicht CLI-Befehle.
- Live-QA mit dem Inspector findet Kern-Bugs, die die CLI-QA übersah ("0 Basilikum" in der Einkaufsliste): Fix gehört in die CLI, dann Patch-Release.
- `mcp-publisher`-Login (GitHub-JWT) läuft ab. Vor `publish` `mcp-publisher login github` (Device-Flow, braucht Samuel einmal im Browser); keinen fremden Token durchreichen.
- Smithery-Listing braucht Samuels Smithery-Login; Glama liest `glama.json` aus dem öffentlichen Repo.

### Lehre aus dem ersten Live-MCP (Mensa, 03.11.2026)

Der Mensa-MCP läuft als Remote-Server (Streamable HTTP, stateless, ohne Login) unter https://mcp.human-agent-interface.com/mensa/mcp: erst FastAPI-Gateway hinter Cloudflare Tunnel auf der Box, jetzt als Cloudflare Worker. Gründe, warum er live ging: öffentliche API ohne Key (OpenMensa v2) statt HTML-Scraping, nur 3 klar beschriebene read-only Tools mit vollständigen annotations, Nutzer brauchen keine Installation (URL in Claude „Add custom connector“ bzw. `claude mcp add --transport http`), Datenschutz-/Nutzungsseiten (`/privacy`, `/terms`) für Directory-Einreichungen, Test mit offiziellem MCP-SDK-Client gegen die echte API, Anfrage an den API-Betreiber (OpenMensa) zur Erlaubnis/Attribution. Daraus: für jeden öffentlichen Dienst zuerst prüfen, ob eine Remote-Variante unter `mcp.human-agent-interface.com/<name>/mcp` möglich ist.

## Parallele Lanes

Mehrere Repos laufen gleichzeitig, jede Lane arbeitet seriell nur in eigenen Repos.

| Thema | Regel |
|---|---|
| Lane | `lane.sh <nr> <repo>...`; eine Lane fasst nur ihre eigenen Repos an. |
| Temp und Marker | `TMPDIR=<repo>/scratch/tmp`, eigene `scratch/`-Marker je Repo. |
| Fake-Server | je Gate-Lauf ein freier Zufallsport (`free_local_port`), daher keine Port-Kollision. |
| Gemeinsame Dateien | `agent-learnings` und Template nur lesen; Änderungen in eigener Klon-Kopie und per Rebase pushen. |
| RAM-Admission | über `hermes-run.sh` (`HERMES_RUN_BUDGET_MB`); Exit 75 = später erneut, nie umgehen; Lease `HAI_BOX_SLOTS`. |
| Modellwahl | je Stufe mit 45-s-Probe: `opencode-go/deepseek-v4.1-flash` (bezahlt), dann `deepseek-v4.1-flash-free`, `glm-5.3-flash-free`, `mimo-v2.6-flash-free`. Go mit 429/Usage-Limit → Grund in den Status, für eine Stunde Gratis. „Free usage limit reached“ lässt opencode still hängen, deshalb Probe vor jeder Stufe. |
| Richtwert | 3 Lanes bei 15 GB RAM. |

## Warum

- `hochschulsport-cli` bestand 18 von 19 Tests, war aber für Menschen unbedienbar.
- Es gab keinen `login`-Befehl, nur fünf Env-Variablen, Kursnummer statt Name, nach `pip` kein Eintrag im PATH, und `book --confirm` sendete nur den ersten Formularschritt.
- Eine Textregel in `rules/AGENTS.md` („Bedienbarkeit für Menschen“) hat das nicht verhindert, weil sie nicht maschinell geprüft wurde.
- Heute fangen das vier Gates: UX02 (kein `login`), UX04 (Pflicht-Option statt Suchbegriff), UX06 (Schnellstart mit Kommentarzeile), UX08 (nur erster Formularschritt).

## Grok-Bot-Budget

Recherche, Erkundung und Bau laufen über opencode. Grok Bot verteilt nur Aufgaben und liest Berichte; er recherchiert nicht, erkundet nicht, baut nicht und fixt nicht.

| Aufgabe | Wer | Budget |
|---|---|---|
| Thema und Demand prüfen | opencode | eine Recherche je Thema |
| Nachfrage-Recherche | Gemini CLI (`gemini --skip-trust -m gemini-3.8-flash`) oder opencode | eine je Kandidat |
| Live-Erkundung und UX-Spec | opencode | eine Erkundung je Tool, Nachbesserung nur bei geändertem Formular |
| Bau und Fixes | opencode | kleine Schritte mit Commit und pytest |
| MCP-Server bauen | opencode | wie CLI-Bau |
| Verteilen und Status lesen | Grok Bot | eine Orchestrierungs-Nachricht je Schritt, eine Zusammenfassung am Ende |
