#!/usr/bin/env python3
"""Qualify the M8.2 native Amiga startup/HAL contract."""

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "config" / "m8-amiga-ocs-68000.json"
HEADER = ROOT / "src" / "amiga" / "m8_startup_contract.h"
OUT = ROOT / "build" / "m8" / "startup"

REQUIRED_TOKENS = (
    "libretos_amiga_reset_entry",
    "libretos_amiga_vectors_init",
    "libretos_amiga_exceptions_init",
    "libretos_amiga_memory_discover",
    "libretos_amiga_serial_init",
    "libretos_amiga_serial_putc",
    "libretos_amiga_serial_puts",
    "libretos_amiga_halt",
    "LIBRETOS_AMIGA_CUSTOM_BASE",
    "LIBRETOS_AMIGA_CIAA_BASE",
    "LIBRETOS_AMIGA_CIAB_BASE",
)


def fail(message: str) -> None:
    print(f"M8.2 Amiga startup/HAL: FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    if not PROFILE.is_file():
        fail("missing canonical M8.1 profile")
    if not HEADER.is_file():
        fail("missing startup/HAL contract")

    profile = json.loads(PROFILE.read_text())
    if profile.get("id") != "amiga-ocs-68000-1m":
        fail("unexpected Amiga profile id")
    if profile.get("machine", {}).get("cpu") != "68000":
        fail("M8.2 baseline must remain 68000")
    if profile.get("machine", {}).get("chipset") != "OCS":
        fail("M8.2 baseline must remain OCS")
    if profile.get("boot", {}).get("kickstart_required") is not False:
        fail("native startup must not require proprietary Kickstart")
    if profile.get("qualification", {}).get("native_68k") is not True:
        fail("profile does not require native 68k execution")

    text = HEADER.read_text()
    missing = [token for token in REQUIRED_TOKENS if token not in text]
    if missing:
        fail("startup contract missing: " + ", ".join(missing))

    evidence = {
        "schema": 1,
        "milestone": "M8.2",
        "status": "PASS",
        "profile": profile["id"],
        "cpu": "68000",
        "chipset": "OCS",
        "contract": [
            "reset-entry",
            "vector-table",
            "exception-baseline",
            "chip-fast-memory-discovery",
            "serial-diagnostics",
            "halt-path",
        ],
        "kickstart_required": False,
        "qualification_boundary": "static startup/HAL contract; runtime boot follows in M8.3",
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "RESULT.json").write_text(json.dumps(evidence, indent=2) + "\n")
    (OUT / "RESULT.txt").write_text(
        "M8.2 Amiga native startup/HAL contract: PASS\n"
        "profile=amiga-ocs-68000-1m\n"
        "cpu=68000 chipset=OCS kickstart_required=false\n"
        "runtime_boot=deferred-to-M8.3\n"
    )
    print("M8.2 Amiga native startup/HAL contract: PASS")


if __name__ == "__main__":
    main()
