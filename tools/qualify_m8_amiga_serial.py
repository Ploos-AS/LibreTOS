#!/usr/bin/env python3
"""Qualify the M8.7 native Amiga serial diagnostics HAL contract."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "config" / "m8-amiga-ocs-68000.json"
STARTUP = ROOT / "src" / "amiga" / "m8_startup_contract.h"
INTERRUPT = ROOT / "src" / "amiga" / "m8_interrupt_contract.h"
SERIAL = ROOT / "src" / "amiga" / "m8_serial_contract.h"
OUT = ROOT / "build" / "m8" / "serial"

def fail(message):
    print(f"M8.7 Amiga serial contract: FAIL ({message})", file=sys.stderr)
    raise SystemExit(1)

def main():
    for path in (PROFILE, STARTUP, INTERRUPT, SERIAL):
        if not path.is_file():
            fail("missing " + str(path.relative_to(ROOT)))
    profile = json.loads(PROFILE.read_text())
    if profile.get("id") != "amiga-ocs-68000-1m":
        fail("unexpected profile id")
    text = SERIAL.read_text()
    required = (
        "LIBRETOS_AMIGA_SERIAL_CUSTOM_BASE",
        "LIBRETOS_AMIGA_SERDATR_OFFSET",
        "LIBRETOS_AMIGA_SERDAT_OFFSET",
        "LIBRETOS_AMIGA_SERPER_OFFSET",
        "LIBRETOS_AMIGA_SERIAL_TX_READY",
        "LIBRETOS_AMIGA_SERIAL_STOP_BIT",
        "libretos_amiga_serial_state",
        "libretos_amiga_serial_hal_init",
        "libretos_amiga_serial_tx_ready",
        "libretos_amiga_serial_hal_putc",
        "libretos_amiga_serial_hal_puts",
        "libretos_amiga_serial_hal_shutdown",
    )
    for symbol in required:
        if symbol not in text:
            fail("missing contract symbol: " + symbol)
    for value in ("0x00dff000ul", "0x0018ul", "0x0030ul", "0x0032ul"):
        if value not in text:
            fail("serial register contract drifted: " + value)
    OUT.mkdir(parents=True, exist_ok=True)
    result = {
        "schema": 1,
        "milestone": "M8.7",
        "status": "PASS",
        "profile": profile["id"],
        "gate": "serial-hal-contract",
        "runtime": "PENDING_AMIGA_RUNTIME_Q3",
        "proprietary_rom_required": False,
        "proprietary_os_required": False,
    }
    (OUT / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("M8.7 Amiga serial contract: PASS (runtime gate pending)")

if __name__ == "__main__":
    main()
