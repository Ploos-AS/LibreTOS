#!/usr/bin/env python3
"""Aggregate M4 qualification gate for canonical Mega ST and Mega STe profiles."""
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build" / "m4" / "qualification"
MEGAST_PROFILE = ROOT / "config" / "m4-mega-st-68000.json"
MEGASTE_PROFILE = ROOT / "config" / "m4-mega-ste-68000.json"

STAGES = [
    ("M4.1", "profiles", ["make", "qualify-m4-profiles"]),
    ("M4.2", "boot", ["make", "qualify-m4-boot"]),
    ("M4.3", "platform", ["make", "qualify-m4-platform"]),
]


def write_result(profiles: list[dict], results: list[dict], status: str) -> None:
    payload = {
        "schema": 1,
        "milestone": "M4.4",
        "status": status,
        "profiles": [profile["id"] for profile in profiles],
        "compatibility_claim": (
            "qualified only for the explicit canonical Mega ST and Mega STe profiles "
            "and the M4.1-M4.3 regressions"
        ),
        "results": results,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "RESULT.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (OUT / "PROFILES.json").write_text(
        json.dumps(profiles, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def main() -> None:
    for profile_path in (MEGAST_PROFILE, MEGASTE_PROFILE):
        if not profile_path.is_file():
            raise SystemExit(f"M4.4: canonical profile missing: {profile_path}")

    profiles = [
        json.loads(MEGAST_PROFILE.read_text(encoding="utf-8")),
        json.loads(MEGASTE_PROFILE.read_text(encoding="utf-8")),
    ]
    expected = ["mega-st-68000-4m-192k-us", "mega-ste-68000-4m-256k-us"]
    actual = [profile.get("id") for profile in profiles]
    if actual != expected:
        raise SystemExit(f"M4.4: unexpected canonical profile ids: {actual}")

    results = []
    for milestone, name, command in STAGES:
        print(f"M4.4: running {milestone} {name}", flush=True)
        cp = subprocess.run(command, cwd=ROOT, check=False)
        result = {
            "milestone": milestone,
            "name": name,
            "status": "PASS" if cp.returncode == 0 else "FAIL",
            "returncode": cp.returncode,
        }
        results.append(result)
        if cp.returncode != 0:
            write_result(profiles, results, "FAIL")
            raise SystemExit(cp.returncode)

    write_result(profiles, results, "PASS")
    print("M4.4 Mega ST family qualification: PASS")


if __name__ == "__main__":
    main()
