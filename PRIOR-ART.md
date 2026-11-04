# PRIOR-ART

Stand 04.11.2026. Recherche durch opencode (deepseek-v4.1-flash-free), weil Gemini mit 429 abbrach. Alle Links per HTTP 200 geprüft.

**Korrektur gegenüber der Rohrecherche:** `mcp-publisher` ist für uns doch relevant, weil die MCP-Server öffentlich in die MCP-Registry und auf Smithery sollen (Geschäftsmodell). Empfehlung dort: einbinden für den Veröffentlichungsschritt.

| Tool | Link (verifiziert) | deckt ab | Empfehlung & Begründung |
|---|---|---|---|
| Restish | https://github.com/rest-sh/restish | A CLI-Gen | einbinden – Guter generischer OpenAPI-CLI-Runner zum Erkunden von APIs, erzeugt aber keinen Python-Code für unsere eigenen CLIs. |
| openapi-cli-generator (danielgtaylor) | https://github.com/danielgtaylor/openapi-cli-generator | A CLI-Gen | nicht – Laut Projekt selbst durch Restish abgelöst und Go-basiert, also kein Baustein für unseren Python-Stack. |
| openapi-cli-gen | https://pypi.org/project/openapi-cli-gen | A CLI-Gen | nicht – Alpha-Tool für generische Python-CLIs; unser UX-Gate und Scraping-Fälle ohne OpenAPI-Spec deckt es nicht ab. |
| OpenAPI Generator | https://openapi-generator.tech/docs/usage | A Client-Gen | einbinden – Reif für typisierte Clients aus vorhandenen Specs, aber nur bei echten APIs relevant, nicht bei HTML-Scraping. |
| Speakeasy CLI | https://www.speakeasy.com/docs/cli-generation/create-cli | A CLI-Gen | nicht – Account-, Go- und Hosting-Kontext sind für tägliche kleine Python-CLIs unnötig schwer. |
| Stainless CLI | https://www.stainless.com/docs/cli/ | A CLI-Gen | nicht – Proprietärer/gehosteter Generator mit Go-SDK-Fokus, kein Open-Source-Baustein für unsere Pipeline. |
| FastMCP | https://github.com/PrefectHQ/fastmcp | B MCP | übernehmen – Ersetzt unseren Eigenbau für MCP-Transport und Tools und kann CLI-Aufrufe direkt als Python-Tools wrappen. |
| FastMCP.from_openapi | https://gofastmcp.com/integrations/openapi | B MCP | übernehmen – Wenn doch eine OpenAPI-Spec vorliegt, ist das der schnellste Python-Weg zum MCP-Server, danach kuratieren. |
| openapi-mcp-generator | https://github.com/harsha-iiiv/openapi-mcp-generator | B MCP | nicht – Erzeugt TypeScript-Proxyserver; für unseren Python-Stack und die CLI-Wrapping-Fälle nicht passend. |
| mcp-openapi-proxy | https://github.com/matthewhand/mcp-openapi-proxy | B MCP | einbinden – Python-Runtime-Proxy für APIs mit Spec, nützlich als Zwischenlösung ohne eigenen MCP-Code. |
| Speakeasy MCP | https://www.speakeasy.com/docs/standalone-mcp/build-server | B MCP | nicht – Kommerziell/gehostet und auf größere Workflows ausgelegt, nicht für unsere interne Gratis-Pipeline. |
| Stainless MCP | https://www.stainless.com/docs/mcp/ | B MCP | nicht – Teil des proprietären Stainless-SDKs und damit kein offener, leichter Baustein für uns. |
| MCP Inspector | https://github.com/modelcontextprotocol/inspector | B MCP | übernehmen – Der CLI-Modus mit JSON-Ausgabe und Exit-Codes ersetzt unseren eigenen MCP-Smoke-Test-Client. |
| Smithery CLI | https://github.com/smithery-ai/cli | B MCP | nicht – Registry-/Client-Werkzeug, kein Generator; für interne MCP-Server ohne Veröffentlichungsbedarf nicht nötig. |
| Glama | https://glama.ai/ | B MCP | nicht – Registry, Hosting und Web-Inspector sind Discovery-Werkzeuge, kein Build-Baustein für unsere Server. |
| tdqs | https://tdqs.dev/cli | B MCP | übernehmen – Deterministischer `tdqs lint --file tools.json --fail-on error --format json` ohne Modell/Key; die Referenzimplementierung ist identisch zur TDQS-Metrik, mit der Glama jedes Tool bewertet. |
| mcp-schema-lint | https://github.com/bengodgart/mcp-schema-lint | B MCP | nicht – Offline-fähiger Schema-Linter mit guten Regeln, aber eine eigene Metrik statt Glamas TDQS; für unser Gate nicht deckungsgleich. |
| scoremcp | https://scoremcp.dev/ | B MCP | nicht – Liefert 0–100 und Note ohne Modell, bewertet aber nach eigener Metrik; Glama-Noten lassen sich damit nicht reproduzieren. |
| mcp-publisher | https://modelcontextprotocol.io/registry/quickstart | B MCP | nicht – Nur für das Veröffentlichen in der öffentlichen MCP-Registry relevant, nicht für interne Server. |
| Aider Scripting | https://aider.chat/docs/scripting.html | C Agent | nicht – Scripting ist brauchbar, aber opencode ist bereits unser Worker; ein zweiter Agenten-Stack bringt keinen Mehrwert. |
| OpenHands | https://docs.openhands.dev/openhands/usage/cli/quick-start | C Agent | nicht – Die CLI wird laut Doku nicht mehr aktiv gepflegt und der Agent-Canvas-/SDK-Stack ist für unsere Tagespipelines zu schwer. |
| SWE-agent | https://github.com/SWE-agent/SWE-agent | C Agent | nicht – Forschungs- und Benchmark-Harness mit Docker-Fokus, kein leichter headless Tages-Worker. |
| Claude Code headless | https://code.claude.com/docs/en/headless | C Agent | nicht – Nicht Open Source und an ein kostenpflichtiges Modell gebunden; opencode mit Gratis-Modellen passt besser. |
| opencode run | https://opencode.ai/docs/cli/ | C Agent | übernehmen – Das ist bereits unser Worker; die dokumentierte Non-Interactive-Schnittstelle ersetzt eigene Prompt-Loops. |
| GitHub Spec Kit | https://github.github.com/spec-kit/quickstart.html | C Agent | einbinden – Liefert Spec-/Plan-/Tasks-Templates für den Tageslauf, ist aber Prozessrahmen und kein Runtime-Ersatz. |
| just | https://github.com/casey/just | D Runner | übernehmen – Ersetzt verstreute Bash-Einstiegspunkte durch ein versioniertes justfile mit Argumenten und Dependencies. |
| Taskfile | https://taskfile.dev/docs/guide/running-tasks | D Runner | einbinden – YAML-Alternative zu just, aber nur eine Runner-Konvention einführen, nicht beide parallel. |
| GNU parallel | https://savannah.gnu.org/projects/parallel/ | D Runner | übernehmen – Für parallele Tages-Lanes und Testläufe die reifste xargs-Alternative mit guter Job-Steuerung. |
| bats-core | https://github.com/bats-core/bats-core | D Shell-Tests | übernehmen – Ersetzt eigene Bash-Test-Harnesses und liefert TAP/JUnit sowie parallele Läufe über --jobs. |
| ShellCheck | https://github.com/koalaman/shellcheck | D Shell-Tests | übernehmen – Statischer Linter für alle Steuer- und Marker-Skripte, günstig in jede Lane einzubauen. |
| pexpect | https://github.com/pexpect/pexpect | E CLI-UX | übernehmen – Reife PTY-Bibliothek für unsere Fake-Server-Sitzungen, statt einen eigenen expect-Loop zu bauen. |
| pytest-pexpect | https://github.com/novakmi/pytest-pexpect | E CLI-UX | einbinden – Verbindet pexpect mit pytest-Fixtures und Assertions, wenn das UX-Gate ohnehin in pytest läuft. |
| pytest-tmux | https://pytest-tmux.readthedocs.io/en/latest | E CLI-UX | einbinden – Nützlich für Screen- und Zeilen-Assertions in tmux, aber nur als Ergänzung zum pexpect-Gate. |
| tmux | https://github.com/tmux/tmux | E CLI-UX | einbinden – Für interaktive Debug-Sitzungen und capture-pane-Smoke-Tests, nicht als primäre Test-Engine. |
| expect | https://expect.sourceforge.net/ | E CLI-UX | nicht – Tcl-basiert und für neue Python-Pipelines unnötig; pexpect deckt den Anwendungsfall besser ab. |
| Click CliRunner | https://click.palletsprojects.com/en/stable/testing/ | E CLI-UX | nicht – Nur sinnvoll, wenn die CLI auf Click/Typer basiert; unsere argparse-CLIs profitieren nicht direkt. |
| ptytest | https://pypi.org/project/ptytest | E CLI-UX | nicht – Junges Beta-Projekt; pexpect und pytest-pexpect sind für unseren Bedarf ausgereifter. |
| Termless | https://termless.dev/guide/comparison.html | E CLI-UX | nicht – TypeScript/Vitest-Ökosystem, passt nicht zu unseren Python-CLI-Tests. |

## Top 5

1. **FastMCP (inkl. `from_openapi`) statt eigenem MCP-Layer**: CLI-Befehle als Python-Tools wrappen; nur wenn eine Spec existiert, `FastMCP.from_openapi()` nutzen und das Ergebnis kuratieren.
2. **bats-core + ShellCheck statt eigenem Bash-Testharness**: Shell-Tests als `.bats`-Dateien, `bats --jobs` für Parallelität, ShellCheck als Pflicht-Lint in jeder Lane.
3. **just + GNU parallel statt Ad-hoc-Lane-Dispatcher**: `justfile` für benannte Lanes und Dependencies, GNU parallel für gleichzeitige Worker; die Marker-Dateien bleiben der Zustand.
4. **pexpect + pytest-pexpect (tmux nur ergänzend) statt eigenem PTY-/Expect-Code**: Fake-Server-Sitzungen und Screen-Assertions als pytest-Fälle; tmux für manuelles Debugging und einzelne Smoke-Tests.
5. **opencode run + MCP Inspector (CLI) statt eigener Agenten- und JSON-RPC-Testclients**: opencode bleibt der Worker, `opencode run` liefert die headless-Schnittstelle, der Inspector prüft MCP-Server per CLI mit JSON und Exit-Codes.

## Folgen für die Iterationen

- **Iteration 1 (jetzt):** ein Repo, Workflow + UX-Gate mit Historie, `pipeline/health.sh` mit Tests. Kein Eigenbau über das hinaus.
- **Iteration 2 (erst wenn Iteration 1 im Betrieb hält):** `health.sh` vor jede Stufe der laufenden Kette hängen; Shell-Tests auf bats-core umstellen, ShellCheck als Pflicht; Kettenskripte ins Repo, Lanes über GNU parallel und Einstieg über ein `justfile` statt eigenem `factory.sh`-Dispatcher; MCP-Server mit FastMCP, Smoke-Test mit MCP Inspector CLI, Veröffentlichung mit mcp-publisher.
- **Später:** UX-Sitzungen auf pexpect umstellen, Vorlage aus cli-mcp-template hierher ziehen.
