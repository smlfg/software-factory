#!/usr/bin/env bash
# Shell-Tests für health.sh, ohne Netz und ohne echte Modelle (Fakes für opencode/gh/meminfo).
set -u
unset OPENCODE_GO_API_KEY OPENCODE_API_KEY   # echte Keys nie in Tests
H=$(cd "$(dirname "$0")/.." && pwd)/health.sh
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
PASS=0; FAIL=0
ok(){ PASS=$((PASS+1)); echo "ok   $1"; }; nok(){ FAIL=$((FAIL+1)); echo "FAIL $1"; }
mkfake(){ # $1=name $2=body
  printf '#!/usr/bin/env bash\n%s\n' "$2" > "$T/$1"; chmod +x "$T/$1"; }
mem(){ printf 'MemAvailable: %s kB\nSwapTotal: %s kB\nSwapFree: %s kB\n' "$1" "$2" "$3" > "$T/meminfo"; }
run(){ ( export FACTORY_STATE_DIR=$T/state OPENCODE_BIN=$T/opencode GH_BIN=$T/gh MEMINFO=$T/meminfo HEALTH_DISK_PATH=$T HEALTH_MIN_DISK_MB=1 HEALTH_TIMEOUT_S=${TO:-5} OPENCODE_GO_ENV=${GOENV:-$T/go.env}; if [ "${FM-x}" = DEFAULT ]; then unset FACTORY_MODELS; else export FACTORY_MODELS="${FM:-m/a m/b m/c}"; fi; "$H" ) > "$T/out" 2> "$T/err"; echo $? > "$T/rc"; }
rc(){ cat "$T/rc"; }
mkfake gh 'exit 0'; mem 8000000 8000000 8000000

# 1: erstes Modell antwortet
mkfake opencode 'echo OK'; run
[ "$(rc)" = 0 ] && [ "$(cat $T/out)" = m/a ] && grep -q "Status: OK" $T/state/STATUS.md && ok "erstes Modell gewählt" || nok "erstes Modell gewählt"
# 2: Fallback auf zweites Modell, wenn erstes Kontingent erschöpft
mkfake opencode '[ "$3" = m/a ] && { echo "Free usage limit reached"; exit 1; }; echo OK'; run
[ "$(rc)" = 0 ] && [ "$(cat $T/out)" = m/b ] && grep -q "Kontingent" $T/state/STATUS.md && ok "Fallback auf m/b" || nok "Fallback auf m/b"
# 3: hängendes Modell -> Timeout, kein Hängen der Pipeline
mkfake opencode '[ "$3" = m/c ] && { echo OK; exit 0; }; sleep 60'
S=$(date +%s); TO=2 run; D=$(( $(date +%s)-S ))
[ "$(rc)" = 0 ] && [ "$(cat $T/out)" = m/c ] && [ $D -lt 20 ] && grep -q "Timeout" $T/state/STATUS.md && ok "Timeout statt Hängen (${D}s)" || nok "Timeout statt Hängen (${D}s, rc=$(rc))"
# 4: kein Modell -> Exit 2, STATUS.md FAIL, Grund auf stderr
mkfake opencode 'echo "Error: Session not found"; exit 1'; run
[ "$(rc)" = 2 ] && [ ! -s $T/out ] && grep -q "Status: FAIL" $T/state/STATUS.md && grep -q "Session not found" $T/state/STATUS.md && grep -q "kein Modell" $T/err && ok "kein Modell -> Exit 2 + STATUS.md" || nok "kein Modell -> Exit 2"
# 5: zu wenig RAM -> Exit 3, Modelle werden gar nicht erst gefragt
mkfake opencode 'touch '"$T"'/called; echo OK'; rm -f $T/called; mem 500000 8000000 8000000; run
[ "$(rc)" = 3 ] && [ ! -f $T/called ] && grep -q "RAM" $T/err && ok "RAM-Mangel -> Exit 3" || nok "RAM-Mangel -> Exit 3"
# 6: Swap voll -> Exit 3
mem 8000000 1000000 10000; run
[ "$(rc)" = 3 ] && grep -q "Swap" $T/err && ok "Swap voll -> Exit 3" || nok "Swap voll -> Exit 3"
# 7: gh nicht eingeloggt -> Exit 4
mem 8000000 8000000 8000000; mkfake gh 'exit 1'; run
[ "$(rc)" = 4 ] && grep -q "gh auth login" $T/err && ok "gh fehlt -> Exit 4" || nok "gh fehlt -> Exit 4"
# 8: HEALTH_SKIP überspringt gh
( export HEALTH_SKIP=gh; run ); [ "$(rc)" = 0 ] && ok "HEALTH_SKIP=gh" || nok "HEALTH_SKIP=gh"
# 9: keine Probe-Verzeichnisse bleiben liegen
[ -z "$(ls -d $T/state/probe.* 2>/dev/null)" ] && ok "Probe-Verzeichnis aufgeräumt" || nok "Probe-Verzeichnis aufgeräumt"

# 10: Default-Reihenfolge: bezahltes opencode Go zuerst
mkfake gh 'exit 0'
printf 'OPENCODE_GO_API_KEY=fake-test-key\n' > $T/go.env; chmod 600 $T/go.env
mkfake opencode 'echo "$3" >> '"$T"'/order; echo OK'; rm -f $T/order; FM=DEFAULT run
[ "$(rc)" = 0 ] && [ "$(cat $T/out)" = opencode-go/deepseek-v4.1-flash ] && ok "Default: Go zuerst" || nok "Default: Go zuerst ($(cat $T/out))"
# 11: Key nur für opencode-go/*, nie für Gratis-Modelle, nie in STATUS.md/stdout
mkfake opencode 'echo "$3 key=${OPENCODE_API_KEY:-none} go=${OPENCODE_GO_API_KEY:-none}" >> '"$T"'/keys; [ "$3" = opencode-go/x ] && exit 1; echo OK'
rm -f $T/keys; FM="opencode-go/x m/b" run
grep -q "^opencode-go/x key=fake-test-key" $T/keys && grep -q "^m/b key=none go=none" $T/keys && ! grep -rq fake-test-key $T/state $T/out $T/err && ok "Go-Key nur für Go, nicht geloggt" || nok "Go-Key nur für Go ($(cat $T/keys))"
# 12: Go mit 429/Limit -> Fallback auf Gratis, Grund in STATUS.md
mkfake opencode '[ "$3" = opencode-go/x ] && { echo "Error: 429 Too Many Requests"; exit 1; }; echo OK'; FM="opencode-go/x m/b" run
[ "$(rc)" = 0 ] && [ "$(cat $T/out)" = m/b ] && grep -q "opencode-go/x | FAIL | Kontingent" $T/state/STATUS.md && ok "Go-Limit -> Fallback Gratis" || nok "Go-Limit -> Fallback Gratis"
# 13: Key-Datei fehlt -> Go übersprungen mit Grund, Gratis antwortet
mkfake opencode 'echo OK'; GOENV=$T/nope.env FM="opencode-go/x m/b" run
[ "$(rc)" = 0 ] && [ "$(cat $T/out)" = m/b ] && grep -q "Go-Key fehlt" $T/state/STATUS.md && ok "ohne Key -> Gratis" || nok "ohne Key -> Gratis"

echo "$PASS passed, $FAIL failed"; [ $FAIL = 0 ]
