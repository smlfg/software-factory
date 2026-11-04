# MCP-NEXT – Rangliste MCP-Server (Stand 04.11.2026)

Methode: demand-first-gate (bestehende MCP-Server auf GitHub/MCP-Registry, Server-Wünsche in modelcontextprotocol/servers, Reddit-Schmerz). Recherche: opencode deepseek-v4.1-flash-free (Gemini: 429-Quota). Rohdaten: work/mcp/research/ra/RESULT-A.md, rb/RESULT-B.md. Alle GitHub-Links per `gh api` geprüft (Sterne/Push unten aktuell). Reddit-JSON war von der Box aus 403-blockiert; Reddit-Links stammen aus Websuche, nicht per API verifiziert. In modelcontextprotocol/servers gab es für keinen Kandidaten ein Request-Issue.
Regel: gate-grüne eigene CLI zuerst (easy win: gleicher Kern, FastMCP-Schicht), dann neue Dienste.

| # | Kandidat | Status CLI | Bestehende MCP-Server | Nachfrage-Beleg | GO/NO-GO | Geschäftsmodell |
|---|---|---|---|---|---|---|
| 1 | chefkoch | gate-grün | keiner auf GitHub (nur GitLab-Snippet https://gitlab.com/-/snippets/4877335) | https://www.reddit.com/r/PythonLearning/comments/1nwtyx4/ | **GO** – öffentliche v2-API ohne Login, Lücke total | Remote-Version mcp.human-agent-interface.com/chefkoch/mcp; Paid Tier Wochenplan/Einkaufslisten-Export; Affiliate/Retail-Media |
| 2 | mensa | gate-grün, Remote-MCP live seit 03.11. | https://github.com/virtUOS/mensa-mcp (0★), https://github.com/allesklardy/munich-mensa-mcp (0★, 2025) | https://www.reddit.com/r/Regensburg/comments/5u977m/ | **GO** – live; offen: Registry-Eintrag io.github.smlfg/mensa, Smithery, Claude-Directory | B2B für Studierendenwerke (Speiseplan-Publishing in Agenten), gehostet |
| 3 | angebote (kaufDA) | Nachrüstung läuft (Lane 3) | https://github.com/vertexitde/kaufda-mcp (0★) | https://www.reddit.com/r/de_EDV/comments/1svqdrm/ (55 Punkte, 39 Kommentare) | **GO** – stärkste Nachfrage; bauen sobald CLI-Gate grün | Retail-Media/Affiliate, Paid Preis-Monitoring, B2B-Datenfeed |
| 4 | hisinone | gate-grün | https://github.com/frederikbeimgraben/hisinone-mcp (1★, 24.09.) | https://www.reddit.com/r/TechFak/comments/vgi468/ ; kommerzielle Middleware (HIO-Publisher) belegt Zahlungsbereitschaft | **GO** | B2B-SaaS für Hochschulen: gehosteter read-only HISinOne-Connector |
| 5 | Gesetze-im-Internet (neu) | – | https://github.com/floleuerer/deutsche-gesetze-mcp (53★, letzter Push 19.12.2025 = verwaist), https://github.com/Ansvar-Systems/German-law-mcp (23★, 07.07.) | https://www.reddit.com/r/mcp/comments/1wtq6xr/ (36 Punkte) | **GO** – öffentlich, kein Login, remote-tauglich | Abo Rechtsrecherche/Zitationsprüfung/Compliance |
| 6 | Bundestag DIP (neu) | – | https://github.com/metaneutrons/german-legal-mcp (11★, deckt DIP mit ab), https://github.com/SimonBerg255/bundestag-dip-mcp (0★), https://github.com/pipeworx-io/mcp-bundestag-de (0★) | https://github.com/cfischa/elt_data4transformation/issues/113 (28 Kommentare) | **GO** – offizielle API, Key kostenlos | Parlaments-Monitoring/Policy-Alerts als Abo |
| 7 | flixbus | Nachrüstung läuft (Lane 2) | https://github.com/vlad-ds/flixbus-mcp (3★, 2025), https://github.com/adambenhassen/flixbus-mcp (1★) | https://www.reddit.com/r/startups/comments/d0cutg/ (11 Punkte, 21 Kommentare) | **GO** | Affiliate-Provision, Paid Preisalarme |
| 8 | Handelsregister (neu) | – | https://github.com/lexdoudkin/handelsregister-mcp (5★), https://github.com/EliaLesyk/mcp-handelsregister (5★) | https://github.com/nolte/claude-job-search/issues/16 ; https://www.reddit.com/r/OSINT/comments/1t18cbz/ | **GO** – Rate-Limit ~60 Req/h beachten | Firmenverifikations-/KYC-Abo |
| 9 | bibliothek (aDISWeb) | gate-grün (heute 14:26) | https://github.com/tilllt/adisweb-client (0★, mit MCP) | https://www.reddit.com/r/Libraries/comments/2etzmk/ | **GO** (Nische) | B2B für Bibliotheksverbünde |
| 10 | doctolib | gate-grün | https://github.com/esinecan/doctolib-mcp (2★), https://github.com/arvernesmotion/Doctolib-MCP (0★) | https://www.reddit.com/r/programmation/comments/1o9w4ya/ (16 Kommentare) | **GO, zurückgestellt** – Captcha + Chromium, rechtlich heikel | nur mit Partner-API (B2B Praxen) |
| 11 | wg-gesucht | gate-grün, Senden unbewiesen | smlfg/wg-gesucht-mcp existiert; https://github.com/robert-kratz/wg-gesucht-mcp (0★) | https://www.reddit.com/r/germany/comments/4qfi4e/ | **GO, kein Neubau** – eigenen wg-gesucht-mcp auf Gate heben | Freemium + B2B Relocation |
| 12 | ImmoScout24 (neu) | – | https://github.com/wiestju/ImmoScout (6★, 21.07.) | https://www.reddit.com/r/webscraping/comments/1kn1jod/ (38 Punkte) | **GO bedingt** – nur Partner-/Mobile-API | Pro-Abo Suchagent, B2B Makler |
| 13 | ELSTER (neu) | – | https://github.com/lukasschwarz/elster-mcp-server (31★, 13.07.), https://github.com/Infraviored/elster-mcp-server (2★) | https://www.reddit.com/r/Steuern/comments/1w9wimo/ (274 Punkte) | **GO bedingt** – Zertifikat/ERiC, hohes Risiko | ERiC-Integrationslizenz |
| – | splan | gate-grün | keiner | keiner | **NO-GO** | – |
| – | studip | gate-grün | https://github.com/flowun/studip-mcp (1★, aktiv) | kaum | **NO-GO** | – |
| – | hochschulsport | gate-grün | keiner | keiner | **NO-GO** | – |
| – | hochschulstart | Nachrüstung | keiner | nur Frust, keine API | **NO-GO** | – |

Verworfen bei der Suche nach neuen Diensten: Moodle (https://github.com/Faixiang/Moodle-MCP, 116★, aktiv), Tagesschau, WebUntis, Too Good To Go, Lieferando, ADAC, Bundesanzeiger (keine MCP-spezifische Nachfrage oder gut abgedeckt).

Erfolg nur über GitHub-Traffic (`gh api repos/smlfg/<repo>/traffic/views|clones|popular/referrers`) und Smithery-Tool-Calls, nie PyPI-Downloads.
