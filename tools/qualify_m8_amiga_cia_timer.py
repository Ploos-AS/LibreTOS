#!/usr/bin/env python3
"""Qualify the M8.4 native Amiga CIA/timer HAL contract."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "config" / "m8-amiga-ocs-68000.json"
STARTUP = ROOT / "src" / "amiga" / "m8_startup_contract.h"
CIA = ROOT / "src" / "amiga" / "m8_cia_timer_contract.h"
OUT = ROOT / "build" / "m8" / "cia-timer"

def fail(message):
    print(f"M8.4 Amiga CIA/timer contract: FAIL ({message})", file=sys.stderr)
    raise SystemExit(1)

def main():
    for path in (PROFILE, STARTUP, CIA):
        if not path.is_file(): fail("missing " + str(path.relative_to(ROOT)))
    profile = json.loads(PROFILE.read_text())
    if profile.get("id") != "amiga-ocs-68000-1m": fail("unexpected profile id")
    text = CIA.read_text()
    required = (
        "LIBRETOS_AMIGA_CIAA_BASE", "LIBRETOS_AMIGA_CIAB_BASE",
        "LIBRETOS_AMIGA_CIA_TIMER_A", "LIBRETOS_AMIGA_CIA_TIMER_B",
        "libretos_amiga_cia_init", "libretos_amiga_timer_init",
        "libretos_amiga_timer_ticks", "libretos_amiga_timer_ack",
        "libretos_amiga_timer_shutdown",
    )
    for symbol in required:
        if symbol not in text: fail("missing contract symbol: " + symbol)
    if "0x00bfe001ul" not in text or "0x00bfd000ul" not in text:
        fail("CIA base address contract drifted")
    OUT.mkdir(parents=True, exist_ok=True)
    result = {
        "schema": 1, "milestone": "M8.4", "status": "PASS",
        "profile": profile["id"], "gate": "cia-timer-hal-contract",
        "runtime": "PENDING_AMIGA_RUNTIME_Q3",
        "proprietary_rom_required": False, "proprietary_os_required": False,
    }
    (OUT / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("M8.4 Amiga CIA/timer contract: PASS (runtime gate pending)")

if __name__ == "__main__": main()
