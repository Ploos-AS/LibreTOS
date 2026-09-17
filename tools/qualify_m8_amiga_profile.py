#!/usr/bin/env python3
"""Qualify the canonical M8.1 native Amiga OCS/68000 profile."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "config" / "m8-amiga-ocs-68000.json"
EXPECTED_ID = "amiga-ocs-68000-1m"
EXPECTED_ARTIFACT = "LibreTOS-Amiga-OCS-68000-1M.rom"


def fail(message):
    raise SystemExit("M8.1 Amiga native profile: FAIL: " + message)


def main():
    if not PROFILE.is_file():
        fail("profile missing")
    p = json.loads(PROFILE.read_text())
    if p.get("schema") != 1 or p.get("milestone") != "M8.1":
        fail("schema or milestone mismatch")
    if p.get("id") != EXPECTED_ID:
        fail("profile id mismatch")
    m = p.get("machine", {})
    if m.get("cpu") != "68000" or m.get("chipset") != "OCS":
        fail("baseline must be 68000/OCS")
    if m.get("chip_ram_kib", 0) < 512:
        fail("baseline chip RAM below 512 KiB")
    boot = p.get("boot", {})
    if boot.get("mode") != "native" or boot.get("kickstart_required") is not False:
        fail("target must be native and independent of proprietary Kickstart")
    q = p.get("qualification", {})
    if q.get("native_68k") is not True or q.get("proprietary_kickstart_required") is not False:
        fail("qualification contract mismatch")
    if p.get("rom", {}).get("artifact") != EXPECTED_ARTIFACT:
        fail("canonical Amiga artifact mismatch")

    out = ROOT / "build" / "m8" / "profile"
    out.mkdir(parents=True, exist_ok=True)
    evidence = {
        "schema": 1,
        "milestone": "M8.1",
        "status": "PASS",
        "profile": EXPECTED_ID,
        "artifact": EXPECTED_ARTIFACT,
        "execution": "native-68k",
        "chipset": "OCS",
        "proprietary_kickstart_required": False,
    }
    (out / "RESULT.json").write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
    (out / "RESULT.txt").write_text(
        "M8.1 Amiga native profile: PASS\n"
        f"profile={EXPECTED_ID}\nartifact={EXPECTED_ARTIFACT}\n"
    )
    print("M8.1 Amiga native profile: PASS")
    print(f"profile={EXPECTED_ID}")


if __name__ == "__main__":
    main()
