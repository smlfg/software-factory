# Projektunabhängige Test-Bausteine

## harness/
Aus smlfg/ilias-cli übernommen, enthält nichts ILIAS-Spezifisches:
- `sitecustomize.py`: Netzwerk-Sandbox. Über `PYTHONPATH` in den Subprozess des Tools laden, dann sind nur Verbindungen zu localhost erlaubt und jeder andere Versuch wird protokolliert.
- `leak_check.py`: Sucht ein Geheimnis (roh, URL- und Base64-kodiert) in Ausgaben und Dateibäumen.

## Später
Contract-Tests, die aus Learnings mit `status: offen` entstehen (z. B. „Login-Erfolg braucht Beweis“ als generischer Test gegen einen Fake-Server).
