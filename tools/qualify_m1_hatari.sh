#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
ROM=${ROM:-"$ROOT/build/m1/libretos-m1-st-us.img"}
LOG=${LOG:-"$ROOT/build/m1/hatari.log"}

test -f "$ROM"
command -v hatari >/dev/null

mkdir -p "$(dirname "$LOG")"

RUNNER=()
if command -v xvfb-run >/dev/null; then
    RUNNER=(xvfb-run -a)
fi

set +e
"${RUNNER[@]}" hatari \
    --tos "$ROM" \
    --machine st \
    --memsize 1 \
    --cpulevel 0 \
    --compatible yes \
    --fast-boot no \
    --sound off \
    --confirm-quit no \
    --benchmark \
    --run-vbls 500 \
    --log-file "$LOG"
rc=$?
set -e

if [[ $rc -ne 0 ]]; then
    echo "Hatari M1 smoke test: FAIL (exit $rc)"
    cat "$LOG" || true
    exit "$rc"
fi

if grep -Eqi 'fatal|cannot load.*tos|invalid.*tos|bus error|address error' "$LOG"; then
    echo "Hatari M1 smoke test: FAIL (fatal marker in log)"
    cat "$LOG"
    exit 1
fi

echo "Hatari M1 smoke test: PASS"
