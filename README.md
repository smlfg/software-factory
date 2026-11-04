# software-factory

Die Fabrik hinter den smlfg-CLIs und -MCP-Servern: ein Werkzeug pro Tag für deutsche Web-Dienste (Mensa, StarPlan, Stud.IP, Bibliothek …), gebaut von Gratis-Modellen über [opencode](https://opencode.ai), abgesichert durch ein maschinelles Bedienbarkeits-Gate.

Iteratives Projekt. **Iteration 1** (dieser Stand): Workflow, UX-Gate und Health-Check an einem Ort. Kettensteuerung (`factory.sh`, Lanes) und Vorlage folgen erst, wenn Iteration 1 im Betrieb hält. Vorher wird geprüft, was es schon gibt: [PRIOR-ART.md](PRIOR-ART.md).

## Inhalt

| Pfad | Was |
|---|---|
| [WORKFLOW.md](WORKFLOW.md) | Ablauf eines Werkzeugs: Nachfrage-Check → Live-Erkundung + `docs/UX.md` → Anforderungen/Abnahmetests → Bau → UX-Gate → Pflicht-QA → Push |
| [rules/AGENTS.md](rules/AGENTS.md) | Regeln für die Worker-Modelle |
| [harness/](harness/) | UX-Gate: `ux_check.py` (UX00–UX09), `ux_session.py` (PTY-Sitzungen gegen `fake_server.py`), Selbsttests |
| [template/UX.md](template/UX.md) | Vorlage für die UX-Spec eines neuen Werkzeugs |
| [pipeline/health.sh](pipeline/health.sh) | Vorab-Check vor jeder Stufe: gh-Login, RAM/Swap, Platte, welches Modell antwortet |

## Ein Lauf

1. `pipeline/health.sh` → gibt das erste antwortende Modell aus, sonst Exit ≠ 0 und Grund in `pipeline/state/STATUS.md`.
2. Worker-Stufe mit diesem Modell (opencode), Ergebnis per Marker-Datei abgehakt.
3. Gate: `python3 harness/ux_check.py <repo>` und `python3 harness/ux_session.py <repo>`; nur grün wird gepusht.

## Start

```bash
git clone https://github.com/smlfg/software-factory && cd software-factory
pipeline/health.sh                              # welches Modell läuft gerade?
python3 harness/ux_check.py ../mensa-cli        # Gate gegen ein Werkzeug
```

Tests: `pipeline/tests/test_health.sh` (Bash, ohne Netz) und `cd harness && python3 -m pytest -q`.

Exit-Codes von `health.sh`: 0 ok, 2 kein Modell, 3 RAM/Swap/Platte, 4 GitHub-Login. Schwellen und Modellliste über Env, siehe Kopf von [health.sh](pipeline/health.sh).

## Herkunft

Workflow und Harness stammen samt Git-Historie aus [smlfg/agent-learnings](https://github.com/smlfg/agent-learnings) (dort bleiben die Learnings). Die Werkzeug-Vorlage liegt vorerst weiter in [smlfg/cli-mcp-template](https://github.com/smlfg/cli-mcp-template).

MIT-Lizenz.
