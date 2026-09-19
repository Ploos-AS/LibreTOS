#!/usr/bin/env python3
"""Aggregate M8 native Amiga foundation qualification."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build" / "m8"
STAGES = (
    ("M8.1", "profile/RESULT.json"),
    ("M8.2", "startup/RESULT.json"),
    ("M8.3", "boot/RESULT.json"),
    ("M8.4", "cia-timer/RESULT.json"),
    ("M8.5", "keyboard/RESULT.json"),
    ("M8.6", "interrupt/RESULT.json"),
    ("M8.7", "serial/RESULT.json"),
    ("M8.8", "video/RESULT.json"),
)

def fail(message):
    print("M8 Amiga foundation: FAIL (" + message + ")", file=sys.stderr)
    raise SystemExit(1)

def main():
    results = []
    for milestone, rel in STAGES:
        path = OUT / rel
        if not path.is_file():
            fail("missing evidence " + rel)
        data = json.loads(path.read_text())
        if data.get("milestone") != milestone or data.get("status") != "PASS":
            fail("invalid evidence " + rel)
        results.append({"milestone": milestone, "evidence": rel, "status": "PASS"})

    result = {
        "schema": 1,
        "milestone": "M8",
        "status": "PASS",
        "gate": "native-amiga-foundation-static-contracts",
        "profile": "amiga-ocs-68000-1m",
        "stages": results,
        "runtime": "AMIGA_RUNTIME_Q3_CORE_QUALIFIED",
        "runtime_status": "INFRASTRUCTURE_QUALIFIED_TARGET_EXECUTION_PENDING",
        "proprietary_rom_required": False,
        "proprietary_os_required": False,
        "qualification_boundary": "Static/contract foundation PASS; Ploos-AS/amiga-runtime Q3 core infrastructure is qualified with FS-UAE and Amiberry. LibreTOS target execution evidence remains required before claiming M8 runtime qualification.",
    }
    (OUT / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("M8 Amiga foundation: PASS (static/contracts; amiga-runtime Q3 core available; LibreTOS execution pending)")

if __name__ == "__main__":
    main()
