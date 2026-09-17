#!/usr/bin/env python3
"""Qualify the M8.5 native Amiga keyboard HAL contract."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "config" / "m8-amiga-ocs-68000.json"
STARTUP = ROOT / "src" / "amiga" / "m8_startup_contract.h"
CIA = ROOT / "src" / "amiga" / "m8_cia_timer_contract.h"
KEYBOARD = ROOT / "src" / "amiga" / "m8_keyboard_contract.h"
OUT = ROOT / "build" / "m8" / "keyboard"

def fail(message):
    print(f"M8.5 Amiga keyboard contract: FAIL ({message})", file=sys.stderr)
    raise SystemExit(1)

def main():
    for path in (PROFILE, STARTUP, CIA, KEYBOARD):
        if not path.is_file():
            fail("missing " + str(path.relative_to(ROOT)))
    profile = json.loads(PROFILE.read_text())
    if profile.get("id") != "amiga-ocs-68000-1m":
        fail("unexpected profile id")
    text = KEYBOARD.read_text()
    required = (
        "LIBRETOS_AMIGA_KEYBOARD_CIA_BASE",
        "LIBRETOS_AMIGA_KEYBOARD_RAW_RELEASE",
        "LIBRETOS_AMIGA_KEYBOARD_RAW_CODE_MASK",
        "LIBRETOS_AMIGA_KEYBOARD_QUEUE_SIZE",
        "libretos_amiga_key_event",
        "libretos_amiga_keyboard_init",
        "libretos_amiga_keyboard_irq",
        "libretos_amiga_keyboard_poll",
        "libretos_amiga_keyboard_ack",
        "libretos_amiga_keyboard_shutdown",
    )
    for symbol in required:
        if symbol not in text:
            fail("missing contract symbol: " + symbol)
    if "0x00bfe001ul" not in text:
        fail("CIAA keyboard base address contract drifted")
    OUT.mkdir(parents=True, exist_ok=True)
    result = {
        "schema": 1,
        "milestone": "M8.5",
        "status": "PASS",
        "profile": profile["id"],
        "gate": "keyboard-hal-contract",
        "runtime": "PENDING_AMIGA_RUNTIME_Q3",
        "proprietary_rom_required": False,
        "proprietary_os_required": False,
    }
    (OUT / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("M8.5 Amiga keyboard contract: PASS (runtime gate pending)")

if __name__ == "__main__":
    main()
