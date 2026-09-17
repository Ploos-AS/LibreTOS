#!/usr/bin/env python3
"""Qualify the M8.6 native Amiga interrupt-controller HAL contract."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "config" / "m8-amiga-ocs-68000.json"
STARTUP = ROOT / "src" / "amiga" / "m8_startup_contract.h"
CIA = ROOT / "src" / "amiga" / "m8_cia_timer_contract.h"
KEYBOARD = ROOT / "src" / "amiga" / "m8_keyboard_contract.h"
INTERRUPT = ROOT / "src" / "amiga" / "m8_interrupt_contract.h"
OUT = ROOT / "build" / "m8" / "interrupt"

def fail(message):
    print(f"M8.6 Amiga interrupt contract: FAIL ({message})", file=sys.stderr)
    raise SystemExit(1)

def main():
    for path in (PROFILE, STARTUP, CIA, KEYBOARD, INTERRUPT):
        if not path.is_file():
            fail("missing " + str(path.relative_to(ROOT)))
    profile = json.loads(PROFILE.read_text())
    if profile.get("id") != "amiga-ocs-68000-1m":
        fail("unexpected profile id")
    text = INTERRUPT.read_text()
    required = (
        "LIBRETOS_AMIGA_CUSTOM_BASE",
        "LIBRETOS_AMIGA_INTENAR_OFFSET",
        "LIBRETOS_AMIGA_INTREQR_OFFSET",
        "LIBRETOS_AMIGA_INTENA_OFFSET",
        "LIBRETOS_AMIGA_INTREQ_OFFSET",
        "LIBRETOS_AMIGA_INT_SETCLR",
        "LIBRETOS_AMIGA_INT_MASTER",
        "LIBRETOS_AMIGA_INT_PORTS",
        "LIBRETOS_AMIGA_INT_VERTB",
        "libretos_amiga_interrupt_state",
        "libretos_amiga_interrupt_init",
        "libretos_amiga_interrupt_enable",
        "libretos_amiga_interrupt_disable",
        "libretos_amiga_interrupt_pending",
        "libretos_amiga_interrupt_ack",
        "libretos_amiga_interrupt_shutdown",
    )
    for symbol in required:
        if symbol not in text:
            fail("missing contract symbol: " + symbol)
    for value in ("0x00dff000ul", "0x001cul", "0x001eul", "0x009aul", "0x009cul"):
        if value not in text:
            fail("custom interrupt register contract drifted: " + value)
    OUT.mkdir(parents=True, exist_ok=True)
    result = {
        "schema": 1,
        "milestone": "M8.6",
        "status": "PASS",
        "profile": profile["id"],
        "gate": "interrupt-hal-contract",
        "runtime": "PENDING_AMIGA_RUNTIME_Q3",
        "proprietary_rom_required": False,
        "proprietary_os_required": False,
    }
    (OUT / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("M8.6 Amiga interrupt contract: PASS (runtime gate pending)")

if __name__ == "__main__":
    main()
