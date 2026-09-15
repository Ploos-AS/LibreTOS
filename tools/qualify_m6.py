#!/usr/bin/env python3
"""Aggregate M6 qualification gate for the canonical Atari Falcon030 profile."""
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build" / "m6" / "qualification"
PROFILE = ROOT / "config" / "m6-falcon030-68030.json"
TARGETS = ROOT / "config" / "targets.json"

STAGES = [
    ("M6.1", "profile", ["make", "qualify-m6-profile"]),
    ("M6.2", "boot", ["make", "qualify-m6-boot"]),
    ("M6.3", "platform", ["make", "qualify-m6-platform"]),
    ("M6.4", "enhanced", ["make", "qualify-m6-enhanced"]),
    ("M6.5", "target-matrix", ["make", "qualify-target-matrix"]),
]


def write_result(profile: dict, results: list[dict], status: str) -> None:
    payload = {
        "schema": 1,
        "milestone": "M6.5",
        "status": status,
        "profile": profile["id"],
        "target": "falcon030-68030",
        "compatibility_claim": (
            "qualified only for the explicit canonical Falcon030 profile and the "
            "M6.1-M6.4 regressions; DSP execution semantics, IDE read/write semantics, "
            "NVRAM persistence, and external audio fidelity remain outside the required runtime claim"
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
        raise SystemExit(f"M6.5: canonical profile missing: {PROFILE}")
    if not TARGETS.is_file():
        raise SystemExit(f"M6.5: target registry missing: {TARGETS}")

    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    if profile.get("id") != "falcon030-68030-4m-512k-us":
        raise SystemExit(f"M6.5: unexpected canonical profile id: {profile.get('id')}")

    registry = json.loads(TARGETS.read_text(encoding="utf-8"))
    matches = [t for t in registry.get("targets", []) if t.get("id") == "falcon030-68030"]
    if len(matches) != 1:
        raise SystemExit("M6.5: Falcon030 target registry entry missing or duplicated")
    target = matches[0]
    if target.get("profile") != "config/m6-falcon030-68030.json":
        raise SystemExit("M6.5: Falcon030 registry/profile mismatch")
    if target.get("artifact") != "LibreTOS-Falcon030-68030-512k-us.img":
        raise SystemExit("M6.5: Falcon030 registry/artifact mismatch")

    results = []
    for milestone, name, command in STAGES:
        print(f"M6.5: running {milestone} {name}", flush=True)
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
    print("M6.5 Atari Falcon030 aggregate qualification: PASS")


if __name__ == "__main__":
    main()
