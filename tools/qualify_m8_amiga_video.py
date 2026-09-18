#!/usr/bin/env python3
"""Qualify the M8.8 native Amiga OCS display HAL contract."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "config" / "m8-amiga-ocs-68000.json"
SERIAL = ROOT / "src" / "amiga" / "m8_serial_contract.h"
VIDEO = ROOT / "src" / "amiga" / "m8_video_contract.h"
OUT = ROOT / "build" / "m8" / "video"

def fail(message):
    print(f"M8.8 Amiga video contract: FAIL ({message})", file=sys.stderr)
    raise SystemExit(1)

def main():
    for path in (PROFILE, SERIAL, VIDEO):
        if not path.is_file():
            fail("missing " + str(path.relative_to(ROOT)))
    profile = json.loads(PROFILE.read_text())
    if profile.get("id") != "amiga-ocs-68000-1m":
        fail("unexpected profile id")
    text = VIDEO.read_text()
    required = (
        "LIBRETOS_AMIGA_VIDEO_CUSTOM_BASE", "LIBRETOS_AMIGA_DIWSTRT_OFFSET",
        "LIBRETOS_AMIGA_DIWSTOP_OFFSET", "LIBRETOS_AMIGA_DDFSTRT_OFFSET",
        "LIBRETOS_AMIGA_DDFSTOP_OFFSET", "LIBRETOS_AMIGA_BPLCON0_OFFSET",
        "LIBRETOS_AMIGA_BPL1PTH_OFFSET", "LIBRETOS_AMIGA_COLOR00_OFFSET",
        "LIBRETOS_AMIGA_VIDEO_MAX_BITPLANES", "libretos_amiga_video_mode",
        "libretos_amiga_video_state", "libretos_amiga_video_init",
        "libretos_amiga_video_set_bitplane", "libretos_amiga_video_set_color",
        "libretos_amiga_video_enable", "libretos_amiga_video_disable",
        "libretos_amiga_video_shutdown",
    )
    for symbol in required:
        if symbol not in text:
            fail("missing contract symbol: " + symbol)
    for value in ("0x00dff000ul", "0x008eul", "0x0090ul", "0x0092ul",
                  "0x0094ul", "0x0100ul", "0x00e0ul", "0x0180ul", "6u"):
        if value not in text:
            fail("OCS display contract drifted: " + value)
    OUT.mkdir(parents=True, exist_ok=True)
    result = {
        "schema": 1, "milestone": "M8.8", "status": "PASS",
        "profile": profile["id"], "gate": "ocs-display-hal-contract",
        "runtime": "PENDING_AMIGA_RUNTIME_Q3",
        "proprietary_rom_required": False, "proprietary_os_required": False,
    }
    (OUT / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("M8.8 Amiga video contract: PASS (runtime gate pending)")

if __name__ == "__main__":
    main()
