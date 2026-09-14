#!/usr/bin/env python3
"""Aggregate M2 qualification gate for the canonical Atari ST profile."""
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build" / "m2" / "qualification"
PROFILE = ROOT / "config" / "m2-st-68000.json"

STAGES = [
    ("M2.1", "profile", ["make", "qualify-m2-profile"]),
    ("M2.2", "boot", ["make", "qualify-m2-boot"]),
    ("M2.3", "gemdos", ["make", "qualify-m2-gemdos"]),
    ("M2.4", "aes-vdi", ["make", "qualify-m2-aes-vdi"]),
    ("M2.5", "media", ["make", "qualify-m2-media"]),
]


def main() -> None:
    if not PROFILE.is_file():
        raise SystemExit("M2.6: canonical profile missing")
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    results = []
    for milestone, name, command in STAGES:
        print(f"M2.6: running {milestone} {name}", flush=True)
        cp = subprocess.run(command, cwd=ROOT)
        results.append({"milestone": milestone, "name": name, "status": "PASS" if cp.returncode == 0 else "FAIL"})
        if cp.returncode != 0:
            write_result(profile, results, "FAIL")
            raise SystemExit(cp.returncode)
    write_result(profile, results, "PASS")
    print(f"M2.6 Atari ST qualification: PASS ({profile['id']})")


def write_result(profile: dict, results: list, status: str) -> None:
    payload = {
        "schema": 1,
        "milestone": "M2.6",
        "status": status,
        "profile": profile["id"],
        "compatibility_claim": "qualified only for the explicit canonical ST/68000 profile and covered regressions",
        "results": results,
    }
    (OUT / "RESULT.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT / "PROFILE.json").write_text(json.dumps(profile, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
