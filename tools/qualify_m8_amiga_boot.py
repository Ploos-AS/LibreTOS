#!/usr/bin/env python3
"""Qualify the M8.3 native Amiga boot/runtime contract.

M8.3 establishes a reproducible emulator-facing boot gate without requiring
or redistributing proprietary Kickstart/Workbench material. The actual
runtime backend consumes the emitted manifest/evidence.
"""

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "config" / "m8-amiga-ocs-68000.json"
STARTUP = ROOT / "src" / "amiga" / "m8_startup_contract.h"
OUT = ROOT / "build" / "m8" / "boot"


def fail(message: str) -> None:
    print(f"M8.3 Amiga native boot: FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    if not PROFILE.is_file():
        fail("missing canonical M8 Amiga profile")
    if not STARTUP.is_file():
        fail("missing M8.2 startup/HAL contract")

    profile = json.loads(PROFILE.read_text())
    if profile.get("id") != "amiga-ocs-68000-1m":
        fail("unexpected profile id")
    machine = profile.get("machine", {})
    boot = profile.get("boot", {})
    qualification = profile.get("qualification", {})
    if machine.get("cpu") != "68000" or machine.get("chipset") != "OCS":
        fail("M8.3 must retain the OCS/68000 baseline")
    if boot.get("mode") != "native":
        fail("boot mode must be native")
    if boot.get("kickstart_required") is not False:
        fail("proprietary Kickstart must not be required")
    if qualification.get("native_68k") is not True:
        fail("native 68k execution is required")

    startup = STARTUP.read_text()
    for symbol in (
        "libretos_amiga_reset_entry",
        "libretos_amiga_vectors_init",
        "libretos_amiga_memory_discover",
        "libretos_amiga_serial_init",
        "libretos_amiga_halt",
    ):
        if symbol not in startup:
            fail(f"startup prerequisite missing: {symbol}")

    manifest = {
        "schema": 1,
        "milestone": "M8.3",
        "profile": profile["id"],
        "execution": "native-68k",
        "cpu": "68000",
        "chipset": "OCS",
        "boot_mode": "native",
        "kickstart_required": False,
        "proprietary_os_files_required": False,
        "emulator_gate": {
            "class": "Amiga",
            "requirements": [
                "cold-reset-entry-reached",
                "vector-table-initialized",
                "memory-discovery-completed",
                "serial-diagnostics-active",
                "controlled-halt-or-runtime-handoff",
            ],
        },
        "qualification_boundary": (
            "repository/runtime boot contract; emulator backend must prove the "
            "runtime markers before M8.3 is claimed as runtime-qualified"
        ),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "BOOT_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (OUT / "RESULT.json").write_text(json.dumps({
        "schema": 1,
        "milestone": "M8.3",
        "status": "PASS",
        "profile": profile["id"],
        "gate": "boot-contract",
        "runtime_emulator": "PENDING",
        "kickstart_required": False,
    }, indent=2) + "\n")
    print("M8.3 Amiga native boot contract: PASS (runtime emulator gate pending)")


if __name__ == "__main__":
    main()
