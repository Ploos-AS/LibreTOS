#!/usr/bin/env python3
"""M7.1 shared Atari machine-profile contract qualification.

Uses only the Python standard library.  The JSON Schema file is the published
contract; this checker enforces the subset needed by the current profiles and,
critically, verifies that each machine remains a distinct release target.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config"
PROFILES = [
    "m2-st-68000.json",
    "m3-ste-68000.json",
    "m4-mega-st-68000.json",
    "m4-mega-ste-68000.json",
    "m5-tt030-68030.json",
    "m6-falcon030-68030.json",
]
HATARI = {"st", "ste", "megast", "megaste", "tt", "falcon"}
REQUIRED_TOP = {"schema", "id", "milestone", "machine", "rom", "display", "storage", "qualification"}
REQUIRED_MACHINE = {"family", "hatari_machine", "cpu", "cpu_level", "cpu_clock_mhz", "st_ram_kib", "fast_ram_kib"}
REQUIRED_ROM = {"size_kib", "country", "source"}
REQUIRED_QUAL = {"emulator", "compatible_mode", "fast_boot", "sound", "minimum_vbls", "proprietary_atari_rom_required"}


def fail(message):
    raise SystemExit("M7.1 Atari machine-profile schema: FAIL: " + message)


def main():
    schema_path = CONFIG / "machine-profile.schema.json"
    if not schema_path.is_file():
        fail("shared schema missing")
    schema = json.loads(schema_path.read_text())
    if schema.get("title") != "LibreTOS Atari machine profile":
        fail("unexpected schema identity")

    ids = set()
    machines = set()
    for name in PROFILES:
        path = CONFIG / name
        if not path.is_file():
            fail(f"profile missing: {name}")
        p = json.loads(path.read_text())
        missing = REQUIRED_TOP - p.keys()
        if missing:
            fail(f"{name}: missing {sorted(missing)}")
        if p["schema"] != 1:
            fail(f"{name}: schema must be 1")
        if not REQUIRED_MACHINE <= p["machine"].keys():
            fail(f"{name}: incomplete machine contract")
        if not REQUIRED_ROM <= p["rom"].keys():
            fail(f"{name}: incomplete ROM contract")
        if not REQUIRED_QUAL <= p["qualification"].keys():
            fail(f"{name}: incomplete qualification contract")
        if p["machine"]["hatari_machine"] not in HATARI:
            fail(f"{name}: unsupported Hatari machine")
        if p["qualification"]["emulator"] != "Hatari":
            fail(f"{name}: emulator must be Hatari")
        if p["qualification"]["proprietary_atari_rom_required"] is not False:
            fail(f"{name}: proprietary Atari ROM dependency forbidden")
        if p["id"] in ids:
            fail(f"duplicate profile id: {p['id']}")
        ids.add(p["id"])
        machine = p["machine"]["hatari_machine"]
        if machine in machines:
            fail(f"duplicate canonical machine target: {machine}")
        machines.add(machine)

    expected = HATARI
    if machines != expected:
        fail(f"machine matrix mismatch: got {sorted(machines)}")

    print("M7.1 Atari machine-profile schema: PASS")
    print("profiles=" + str(len(PROFILES)))
    print("machines=" + ",".join(sorted(machines)))
    print("policy=separate-machine-builds-and-release-artifacts")


if __name__ == "__main__":
    main()
