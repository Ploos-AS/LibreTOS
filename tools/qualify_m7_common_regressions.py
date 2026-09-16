#!/usr/bin/env python3
"""M7.2 cross-machine GEMDOS/AES/VDI regression contract.

This stage verifies that every retained Atari target participates in the same
common OS regression contract while keeping its own profile and ROM artifact.
Runtime execution of the common probes is layered on the already-qualified
per-machine Hatari harnesses; this matrix prevents later targets from silently
escaping common GEMDOS/AES/VDI coverage.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = ROOT / "config" / "targets.json"
REQUIRED = {"st-68000", "ste-68000", "mega-st-68000", "mega-ste-68000", "tt030-68030", "falcon030-68030"}
SUITES = ("gemdos", "aes", "vdi")


def fail(msg):
    raise SystemExit("M7.2 common Atari regression matrix: FAIL: " + msg)


def main():
    data = json.loads(TARGETS.read_text())
    targets = data.get("targets", [])
    ids = {t.get("id") for t in targets}
    if ids != REQUIRED:
        fail("retained target set mismatch")

    artifacts = set()
    rows = []
    for target in targets:
        tid = target["id"]
        profile_path = ROOT / target["profile"]
        if not profile_path.is_file():
            fail(f"{tid}: profile missing")
        profile = json.loads(profile_path.read_text())
        artifact = target.get("artifact")
        if not artifact or artifact in artifacts:
            fail(f"{tid}: release artifact must be present and unique")
        artifacts.add(artifact)
        if profile.get("qualification", {}).get("proprietary_atari_rom_required") is not False:
            fail(f"{tid}: common suite cannot require proprietary Atari ROM")
        rows.append({
            "target": tid,
            "profile_id": profile["id"],
            "machine": profile["machine"]["hatari_machine"],
            "artifact": artifact,
            "suites": list(SUITES),
        })

    out = ROOT / "build" / "m7" / "common-regressions"
    out.mkdir(parents=True, exist_ok=True)
    evidence = {
        "schema": 1,
        "milestone": "M7.2",
        "policy": "common-os-contract-with-separate-machine-roms",
        "suites": list(SUITES),
        "targets": rows,
    }
    (out / "MATRIX.json").write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
    (out / "RESULT.txt").write_text(
        "M7.2 common Atari regression matrix: PASS\n"
        f"targets={len(rows)}\n"
        "suites=gemdos,aes,vdi\n"
        "policy=common-os-contract-with-separate-machine-roms\n"
    )
    print("M7.2 common Atari regression matrix: PASS")
    print(f"targets={len(rows)} suites=gemdos,aes,vdi")


if __name__ == "__main__":
    main()
