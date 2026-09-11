#!/usr/bin/env python3
from pathlib import Path
import sys

required = [
    Path("README.md"),
    Path("Makefile"),
    Path("docs/ROADMAP.md"),
    Path("docs/PROVENANCE.md"),
]

missing = [str(path) for path in required if not path.is_file()]
if missing:
    print("M0 FAIL: missing required files:")
    for path in missing:
        print(f"  - {path}")
    sys.exit(1)

readme = Path("README.md").read_text(encoding="utf-8")
provenance = Path("docs/PROVENANCE.md").read_text(encoding="utf-8")

checks = {
    "Atari ST target": "Atari ST" in readme,
    "68000 target": "68000" in readme,
    "Hatari qualification direction": "Hatari" in readme,
    "proprietary ROM exclusion": "proprietary Atari TOS ROM" in provenance,
    "EmuTOS provenance": "EmuTOS" in provenance,
}

failed = [name for name, ok in checks.items() if not ok]
if failed:
    print("M0 FAIL:")
    for name in failed:
        print(f"  - {name}")
    sys.exit(1)

print("LibreTOS M0 qualification: PASS")
for name in checks:
    print(f"  PASS: {name}")
