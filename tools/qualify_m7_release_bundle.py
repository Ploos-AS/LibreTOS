#!/usr/bin/env python3
"""M7.5 multi-model release bundle and Atari-family no-regression gate."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = ROOT / "config" / "targets.json"
EXPECTED = {
    "st-68000", "ste-68000", "mega-st-68000", "mega-ste-68000",
    "tt030-68030", "falcon030-68030",
}


def fail(msg):
    raise SystemExit("M7.5 Atari family release bundle: FAIL: " + msg)


def main():
    registry = json.loads(TARGETS.read_text())
    targets = registry.get("targets", [])
    if {t.get("id") for t in targets} != EXPECTED:
        fail("retained target set mismatch")
    if registry.get("policy", {}).get("retain_all_targets") is not True:
        fail("retain_all_targets policy is not enabled")

    artifacts = set()
    rows = []
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
        rows.append({
            "target": tid,
            "label": target["label"],
            "milestone": target["milestone"],
            "profile_id": profile["id"],
            "machine": profile["machine"]["hatari_machine"],
            "canonical_artifact": artifact,
            "release_role": "required-machine-specific-rom",
        })

    out = ROOT / "build" / "m7" / "release-bundle"
    out.mkdir(parents=True, exist_ok=True)
    evidence = {
        "schema": 1,
        "milestone": "M7.5",
        "status": "PASS",
        "policy": "retain-and-publish-every-qualified-machine-rom",
        "universal_rom": {
            "required": False,
            "role_if_present": "optional-additive-convenience-artifact",
            "may_replace_machine_specific_artifacts": False,
        },
        "required_artifact_count": len(rows),
        "targets": rows,
    }
    (out / "MANIFEST.json").write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
    (out / "RESULT.txt").write_text(
        "M7.5 Atari family release bundle: PASS\n"
        f"targets={len(rows)} artifacts={len(artifacts)}\n"
        "policy=retain-and-publish-every-qualified-machine-rom\n"
        "universal-rom=optional-addition-only\n"
    )
    print("M7.5 Atari family release bundle: PASS")
    print(f"targets={len(rows)} artifacts={len(artifacts)}")


if __name__ == "__main__":
    main()
