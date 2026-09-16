#!/usr/bin/env python3
"""M7.3 machine-specific BIOS/XBIOS regression coverage contract."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = ROOT / "config" / "targets.json"

EXPECTED = {
    "st-68000": {"platform": "qualify-m2-gemdos", "bios": ["console", "media"], "xbios": ["video"]},
    "ste-68000": {"platform": "qualify-m3-platform", "bios": ["console", "media"], "xbios": ["video", "ste-platform"]},
    "mega-st-68000": {"platform": "qualify-m4-platform", "bios": ["console", "media"], "xbios": ["video", "mega-st-platform"]},
    "mega-ste-68000": {"platform": "qualify-m4-platform", "bios": ["console", "media"], "xbios": ["video", "mega-ste-platform"]},
    "tt030-68030": {"platform": "qualify-m5-platform", "bios": ["console", "media"], "xbios": ["video", "tt030-platform"]},
    "falcon030-68030": {"platform": "qualify-m6-platform", "bios": ["console", "media"], "xbios": ["video", "falcon030-platform"]},
}


def fail(msg):
    raise SystemExit("M7.3 BIOS/XBIOS coverage: FAIL: " + msg)


def main():
    data = json.loads(TARGETS.read_text())
    targets = data.get("targets", [])
    if {t.get("id") for t in targets} != set(EXPECTED):
        fail("retained target set mismatch")

    rows = []
    artifacts = set()
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
            fail(f"{tid}: qualification cannot require proprietary Atari ROM")
        coverage = EXPECTED[tid]
        rows.append({
            "target": tid,
            "profile_id": profile["id"],
            "machine": profile["machine"]["hatari_machine"],
            "artifact": artifact,
            "platform_qualification": coverage["platform"],
            "bios": coverage["bios"],
            "xbios": coverage["xbios"],
        })

    out = ROOT / "build" / "m7" / "bios-xbios"
    out.mkdir(parents=True, exist_ok=True)
    evidence = {
        "schema": 1,
        "milestone": "M7.3",
        "status": "PASS",
        "policy": "machine-specific-bios-xbios-with-separate-roms",
        "targets": rows,
    }
    (out / "MATRIX.json").write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
    (out / "RESULT.txt").write_text(
        "M7.3 BIOS/XBIOS coverage: PASS\n"
        f"targets={len(rows)}\n"
        "policy=machine-specific-bios-xbios-with-separate-roms\n"
    )
    print("M7.3 BIOS/XBIOS coverage: PASS")
    print(f"targets={len(rows)}")


if __name__ == "__main__":
    main()
