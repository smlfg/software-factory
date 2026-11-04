#!/usr/bin/env bash
# health.sh – Vorab-Check vor jeder Pipeline-Stufe.
# Prüft gh-Login, RAM/Swap, Platte und welches opencode-Modell antwortet.
# Erfolg: Exit 0, erstes funktionierendes Modell auf stdout.
# Fehler: Exit 2 (kein Modell) / 3 (Ressourcen) / 4 (gh), Grund auf stderr.
# Jedes Ergebnis landet in $FACTORY_STATE_DIR/STATUS.md, damit ein Abbruch sichtbar ist statt still zu hängen.
#
# Env (alle optional):
#   FACTORY_MODELS        Kandidaten in Reihenfolge (Leerzeichen-getrennt).
#                         Default: bezahltes opencode Go zuerst, dann Gratis-Modelle als Fallback.
#   OPENCODE_GO_ENV       Datei mit OPENCODE_GO_API_KEY=… (Default /home/box/.secrets/opencode-go.env, 0600).
#                         Der Key geht nur an opencode-go/*-Proben (als OPENCODE_API_KEY), nie an Gratis-Modelle,
#                         und wird nie ausgegeben.
#   HEALTH_TIMEOUT_S      Timeout je Modell-Probe (Default 45)
#   HEALTH_MIN_AVAIL_MB   Mindestens verfügbarer RAM (Default 1500)
#   HEALTH_MAX_SWAP_PCT   Maximal belegter Swap in % (Default 90)
#   HEALTH_MIN_DISK_MB    Mindestens freier Platz im Arbeitsverzeichnis (Default 5120)
#   HEALTH_DISK_PATH      Pfad für den Platten-Check (Default $HOME)
#   HEALTH_SKIP           Checks überspringen, z.B. "gh disk"
#   FACTORY_STATE_DIR     Default: <repo>/pipeline/state
#   OPENCODE_BIN, GH_BIN, MEMINFO  nur für Tests austauschbar
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
STATE=${FACTORY_STATE_DIR:-$HERE/state}; mkdir -p "$STATE"
MODELS=${FACTORY_MODELS:-"opencode-go/deepseek-v4.1-flash opencode/deepseek-v4.1-flash-free opencode/glm-5.3-flash-free opencode/mimo-v2.6-flash-free"}
GO_ENV=${OPENCODE_GO_ENV:-/home/box/.secrets/opencode-go.env}
T=${HEALTH_TIMEOUT_S:-45}
OPENCODE=${OPENCODE_BIN:-opencode}; GH=${GH_BIN:-gh}; MEMINFO=${MEMINFO:-/proc/meminfo}
SKIP=" ${HEALTH_SKIP:-} "
LINES=()
add(){ LINES+=("| $1 | $2 | $3 |"); }
skip(){ [[ "$SKIP" == *" $1 "* ]]; }
status(){ # $1=OK|FAIL $2=Zusammenfassung
  { echo "# Factory-Status: $1"; echo; echo "Zeit: $(date '+%F %T %Z')  "; echo "Ergebnis: $2"; echo
    echo "| Check | Ergebnis | Detail |"; echo "|---|---|---|"; printf '%s\n' "${LINES[@]}"; } > "$STATE/STATUS.md.tmp" && mv "$STATE/STATUS.md.tmp" "$STATE/STATUS.md"; }
die(){ status FAIL "$2"; echo "health: $2 (Details: $STATE/STATUS.md)" >&2; exit "$1"; }

# 1) GitHub-Login (für Push)
if ! skip gh; then
  if timeout 20 "$GH" auth status >/dev/null 2>&1; then add gh OK "eingeloggt"; else add gh FAIL "gh auth status fehlgeschlagen"; die 4 "GitHub-Login fehlt: gh auth login"; fi
fi
# 2) RAM/Swap
if ! skip ram; then
  kv(){ awk -v k="$1:" '$1==k{print int($2/1024)}' "$MEMINFO"; }
  AV=$(kv MemAvailable); ST=$(kv SwapTotal); SF=$(kv SwapFree); AV=${AV:-0}; ST=${ST:-0}; SF=${SF:-0}
  SP=0; [ "$ST" -gt 0 ] && SP=$(( (ST-SF)*100/ST ))
  if [ "$AV" -lt "${HEALTH_MIN_AVAIL_MB:-1500}" ]; then add ram FAIL "${AV} MB frei"; die 3 "zu wenig RAM frei (${AV} MB)"; fi
  if [ "$SP" -gt "${HEALTH_MAX_SWAP_PCT:-90}" ]; then add swap FAIL "${SP}% belegt"; die 3 "Swap zu ${SP}% belegt"; fi
  add ram OK "${AV} MB frei, Swap ${SP}%"
fi
# 3) Platte
if ! skip disk; then
  FREE=$(df -Pm "${HEALTH_DISK_PATH:-$HOME}" 2>/dev/null | awk 'NR==2{print $4}'); FREE=${FREE:-0}
  if [ "$FREE" -lt "${HEALTH_MIN_DISK_MB:-5120}" ]; then add disk FAIL "${FREE} MB frei"; die 3 "zu wenig Plattenplatz (${FREE} MB)"; fi
  add disk OK "${FREE} MB frei"
fi
# 4) Modelle: erstes, das in T Sekunden mit OK antwortet. Eigenes leeres Verzeichnis, damit keine alte Sitzung stört.
PROBE=$(mktemp -d "$STATE/probe.XXXXXX"); trap 'rm -rf "$PROBE"' EXIT
# Go-Key nur für opencode-go/* in einer Subshell setzen; Gratis-Proben laufen ohne Key.
probe(){ ( cd "$PROBE" || exit 1
  if [[ "$1" == opencode-go/* ]]; then
    if [ -z "${OPENCODE_GO_API_KEY:-}" ] && [ -r "$GO_ENV" ]; then set -a; . "$GO_ENV"; set +a; fi
    [ -n "${OPENCODE_GO_API_KEY:-}" ] || { echo "kein OPENCODE_GO_API_KEY"; exit 78; }
    export OPENCODE_API_KEY=$OPENCODE_GO_API_KEY
  else unset OPENCODE_GO_API_KEY; fi
  timeout -k 5 "$T" "$OPENCODE" run -m "$1" "Antworte nur mit OK" < /dev/null ) 2>&1; }
for m in $MODELS; do
  OUT=$(probe "$m"); RC=$?
  if [ $RC = 0 ] && grep -q OK <<<"$OUT"; then add "$m" OK "antwortet"; status OK "Modell $m"; echo "$m"; exit 0; fi
  if [ $RC = 124 ] || [ $RC = 137 ]; then WHY="Timeout nach ${T}s"
  elif [ $RC = 78 ]; then WHY="Go-Key fehlt ($GO_ENV)"
  elif grep -qiE "usage limit|rate limit|quota|too many requests|429|insufficient (balance|credit)" <<<"$OUT"; then WHY="Kontingent erschöpft"
  elif grep -qi "session not found" <<<"$OUT"; then WHY="Session not found (opencode-Zustand kaputt)"
  else WHY="rc=$RC $(tr '\n|' '  ' <<<"$OUT" | tail -c 120)"; fi
  add "$m" FAIL "$WHY"
done
die 2 "kein Modell antwortet"
