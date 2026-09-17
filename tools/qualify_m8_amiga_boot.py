#!/usr/bin/env python3
"""Qualify the M8.3 native Amiga boot/runtime contract."""

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "config" / "m8-amiga-ocs-68000.json"
RUNTIME = ROOT / "config" / "m8-amiga-runtime.json"
STARTUP = ROOT / "src" / "amiga" / "m8_startup_contract.h"
OUT = ROOT / "build" / "m8" / "boot"


def fail(message: str) -> None:
    print(f"M8.3 Amiga native boot: FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    if not PROFILE.is_file():
        fail("missing canonical M8 Amiga profile")
    if not RUNTIME.is_file():
        fail("missing amiga-runtime integration contract")
    if not STARTUP.is_file():
        fail("missing M8.2 startup/HAL contract")

    profile = json.loads(PROFILE.read_text())
    runtime = json.loads(RUNTIME.read_text())
    if profile.get("id") != "amiga-ocs-68000-1m":
        fail("unexpected profile id")
    machine = profile.get("machine", {})
    boot = profile.get("boot", {})
    qualification = profile.get("qualification", {})
    if machine.get("cpu") != "68000" or machine.get("chipset") != "OCS":
        fail("M8.3 must retain the OCS/68000 baseline")
    if boot.get("mode") != "native" or boot.get("kickstart_required") is not False:
        fail("native free boot contract violated")
    if qualification.get("native_68k") is not True:
        fail("native 68k execution is required")

    if runtime.get("backend") != "Ploos-AS/amiga-runtime":
        fail("unexpected runtime backend")
    if runtime.get("backend_level_required") != "Q3":
        fail("M8.3 requires Q3 emulator/runtime integration")
    if runtime.get("profile") != profile["id"]:
        fail("runtime profile does not match canonical profile")
    if runtime.get("proprietary_rom_required") is not False:
        fail("runtime contract must not require proprietary ROM")
    if runtime.get("proprietary_os_required") is not False:
        fail("runtime contract must not require proprietary OS files")

    startup = STARTUP.read_text()
    required = [
        "cold-reset-entry-reached",
        "vector-table-initialized",
        "memory-discovery-completed",
        "serial-diagnostics-active",
        "controlled-halt-or-runtime-handoff",
    ]
    symbols = (
        "libretos_amiga_reset_entry",
        "libretos_amiga_vectors_init",
        "libretos_amiga_memory_discover",
        "libretos_amiga_serial_init",
        "libretos_amiga_halt",
    )
    for symbol in symbols:
        if symbol not in startup:
            fail(f"startup prerequisite missing: {symbol}")
    if runtime.get("required_markers") != required:
        fail("runtime marker contract drifted")

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
        "runtime_backend": runtime["backend"],
        "runtime_backend_level_required": runtime["backend_level_required"],
        "runtime_command": runtime["command"],
        "emulator_gate": {"class": "Amiga", "requirements": required},
        "qualification_boundary": (
            "LibreTOS handoff is defined; Ploos-AS/amiga-runtime must reach Q3 "
            "and capture all runtime markers before M8.3 runtime PASS"
        ),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "BOOT_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (OUT / "RESULT.json").write_text(json.dumps({
        "schema": 1,
        "milestone": "M8.3",
        "status": "PASS",
        "profile": profile["id"],
        "gate": "boot-contract-and-runtime-handoff",
        "runtime_backend": runtime["backend"],
        "runtime_emulator": "BLOCKED_ON_AMIGA_RUNTIME_M1_M2",
        "kickstart_required": False,
    }, indent=2) + "\n")
    print("M8.3 boot contract/runtime handoff: PASS (amiga-runtime Q3 pending)")


if __name__ == "__main__":
    main()
