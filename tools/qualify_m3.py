#!/usr/bin/env python3
"""Aggregate M3 qualification gate for the canonical Atari STe profile."""
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build" / "m3" / "qualification"
PROFILE = ROOT / "config" / "m3-ste-68000.json"

STAGES = [
    ("M3.1", "profile", ["make", "qualify-m3-profile"]),
    ("M3.2", "boot", ["make", "qualify-m3-boot"]),
    ("M3.3", "platform", ["make", "qualify-m3-platform"]),
    ("M3.4", "enhanced", ["make", "qualify-m3-enhanced"]),
]


def write_result(profile: dict, results: list, status: str) -> None:
    payload = {
        "schema": 1,
        "milestone": "M3.5",
        "status": status,
        "profile": profile["id"],
        "compatibility_claim": (
            "qualified only for the explicit canonical STe/68000 profile "
            "and the M3.1-M3.4 regressions"
        ),
        "results": results,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "RESULT.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (OUT / "PROFILE.json").write_text(
        json.dumps(profile, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def main() -> None:
    if not PROFILE.is_file():
        raise SystemExit("M3.5: canonical STe profile missing")

    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    if profile.get("id") != "ste-68000-1m-256k-us":
        raise SystemExit("M3.5: unexpected canonical STe profile id")

    results = []
    for milestone, name, command in STAGES:
        print(f"M3.5: running {milestone} {name}", flush=True)
        cp = subprocess.run(command, cwd=ROOT, check=False)
        result = {
            "milestone": milestone,
            "name": name,
            "status": "PASS" if cp.returncode == 0 else "FAIL",
            "returncode": cp.returncode,
        }
        results.append(result)
        if cp.returncode != 0:
            write_result(profile, results, "FAIL")
            raise SystemExit(cp.returncode)

    write_result(profile, results, "PASS")
    print(f"M3.5 Atari STe qualification: PASS ({profile['id']})")


if __name__ == "__main__":
    main()
