# Workflow: Website rein, CLI raus

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
| Worker | opencode `deepseek-v4.1-flash-free`, Fallback `glm-5.3-flash-free`, gestartet über `/home/box/scripts/hermes-run.sh` mit Shim |

## Schritt 5: UX-Gate

| Feld | Inhalt |
|---|---|
| Eingabe | fertiger Build, `docs/UX.md`, Fixtures |
| Ausgabe (Dateien) | Markdown-Bericht von `ux_check.py` und `ux_session.py` |
| Gate | `python tests/harness/ux_check.py <repo>`: UX01-UX08 ohne FAIL. `python tests/harness/ux_session.py <repo>`: frisches venv, Befehl im PATH, Login-Prompts, Auswahl per Name, `N` bricht ohne Request ab, `j` gegen Fake-Server sendet ALLE Formularschritte. Kein PASS -> zurück zu Schritt 4. |
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
| Worker | Samuel (Push/Freigabe), opencode (Text und Eintrag) |

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
| Live-Erkundung und UX-Spec | opencode | eine Erkundung je Tool, Nachbesserung nur bei geändertem Formular |
| Bau und Fixes | opencode | kleine Schritte mit Commit und pytest |
| Verteilen und Status lesen | Grok Bot | eine Orchestrierungs-Nachricht je Schritt, eine Zusammenfassung am Ende |
