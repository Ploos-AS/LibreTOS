#!/usr/bin/env python3
"""M7.4 compatibility matrix and qualification boundaries."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = ROOT / "config" / "targets.json"

BOUNDARIES = {
    "st-68000": {"common": ["gemdos", "aes", "vdi", "bios", "xbios-video"], "machine": [], "boundary": "ST baseline"},
    "ste-68000": {"common": ["gemdos", "aes", "vdi", "bios", "xbios-video"], "machine": ["ste-platform", "ste-enhanced"], "boundary": "STe extensions"},
    "mega-st-68000": {"common": ["gemdos", "aes", "vdi", "bios", "xbios-video"], "machine": ["mega-st-platform"], "boundary": "Mega ST platform"},
    "mega-ste-68000": {"common": ["gemdos", "aes", "vdi", "bios", "xbios-video"], "machine": ["mega-ste-platform"], "boundary": "Mega STe platform"},
    "tt030-68030": {"common": ["gemdos", "aes", "vdi", "bios", "xbios-video"], "machine": ["tt030-platform", "tt030-enhanced"], "boundary": "TT030 extensions"},
    "falcon030-68030": {"common": ["gemdos", "aes", "vdi", "bios", "xbios-video"], "machine": ["falcon030-platform", "falcon030-enhanced"], "boundary": "Falcon030 extensions"},
}


def fail(msg):
    raise SystemExit("M7.4 compatibility matrix: FAIL: " + msg)


def main():
    registry = json.loads(TARGETS.read_text())
    targets = registry.get("targets", [])
    if {t.get("id") for t in targets} != set(BOUNDARIES):
        fail("retained target set mismatch")

    rows = []
    artifacts = set()
    for target in targets:
        tid = target["id"]
        if target.get("status") != "qualified":
            fail(f"{tid}: target is not qualified")
        artifact = target.get("artifact")
        if not artifact or artifact in artifacts:
            fail(f"{tid}: canonical artifact missing or duplicated")
        artifacts.add(artifact)
        profile_path = ROOT / target["profile"]
        if not profile_path.is_file():
            fail(f"{tid}: profile missing")
        profile = json.loads(profile_path.read_text())
        if profile.get("qualification", {}).get("proprietary_atari_rom_required") is not False:
            fail(f"{tid}: proprietary Atari ROM required")
        b = BOUNDARIES[tid]
        rows.append({
            "target": tid,
            "profile_id": profile["id"],
            "machine": profile["machine"]["hatari_machine"],
            "artifact": artifact,
            "common_contract": b["common"],
            "machine_specific_contract": b["machine"],
            "qualification_boundary": b["boundary"],
        })

    out = ROOT / "build" / "m7" / "compatibility"
    out.mkdir(parents=True, exist_ok=True)
    evidence = {
        "schema": 1,
        "milestone": "M7.4",
        "status": "PASS",
        "policy": "common-contract-plus-machine-specific-boundaries",
        "universal_rom_policy": "optional-addition-only-never-replacement",
        "targets": rows,
    }
    (out / "MATRIX.json").write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
    (out / "RESULT.txt").write_text(
        "M7.4 compatibility matrix: PASS\n"
        f"targets={len(rows)}\n"
        "policy=common-contract-plus-machine-specific-boundaries\n"
    )
    print("M7.4 compatibility matrix: PASS")
    print(f"targets={len(rows)}")


if __name__ == "__main__":
    main()
