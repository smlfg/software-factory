# software-factory

Die Fabrik hinter den smlfg-CLIs und -MCP-Servern: ein Werkzeug pro Tag für deutsche Web-Dienste (Mensa, StarPlan, Stud.IP, Bibliothek …), gebaut über [opencode](https://opencode.ai): zuerst das bezahlte opencode Go (`opencode-go/deepseek-v4.1-flash`), Gratis-Modelle als Fallback, abgesichert durch ein maschinelles Bedienbarkeits-Gate.

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

## Modelle

Reihenfolge (Default von `FACTORY_MODELS`): `opencode-go/deepseek-v4.1-flash` → `opencode/deepseek-v4.1-flash-free` → `opencode/glm-5.3-flash-free` → `opencode/mimo-v2.6-flash-free`. Jede Probe hat 45 s.

Der Go-Key liegt nur in `/home/box/.secrets/opencode-go.env` (0600, `OPENCODE_GO_API_KEY=…`, Pfad über `OPENCODE_GO_ENV`). Er wird nur für `opencode-go/*`-Aufrufe als `OPENCODE_API_KEY` gesetzt, nie an Gratis-Modelle gegeben und nie ausgegeben. Meldet Go ein Limit (429, Usage-Limit), fällt die Kette auf Gratis zurück und schreibt den Grund in den Status.

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
