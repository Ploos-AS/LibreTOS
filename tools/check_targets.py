#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "config" / "targets.json"


def fail(msg: str) -> None:
    raise SystemExit(f"target-matrix: FAIL: {msg}")


def main() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if data.get("schema") != 1:
        fail("schema must be 1")
    policy = data.get("policy", {})
    if policy.get("single_codebase") is not True or policy.get("retain_all_targets") is not True:
        fail("single-codebase/retain-all-targets policy missing")

    targets = data.get("targets", [])
    expected = [
        "st-68000",
        "ste-68000",
        "mega-st-68000",
        "mega-ste-68000",
        "tt030-68030",
        "falcon030-68030",
    ]
    ids = [t.get("id") for t in targets]
    if ids != expected:
        fail(f"target order/matrix mismatch: {ids!r}")

    seen_artifacts = set()
    for target in targets:
        for key in ("id", "label", "milestone", "status", "profile", "cpu", "rom_kib", "country", "artifact"):
            if key not in target:
                fail(f"{target.get('id', '<unknown>')}: missing {key}")
        artifact = target["artifact"]
        if artifact in seen_artifacts:
            fail(f"duplicate artifact name {artifact}")
        seen_artifacts.add(artifact)
        if not artifact.startswith("LibreTOS-") or not artifact.endswith(".img"):
            fail(f"invalid artifact name {artifact}")
        if target["status"] not in {"planned", "implemented", "qualified"}:
            fail(f"{target['id']}: invalid status {target['status']}")

    st = targets[0]
    if st["status"] != "qualified":
        fail("ST target must remain qualified")
    st_profile = ROOT / st["profile"]
    if not st_profile.is_file():
        fail("qualified ST profile missing")
    profile = json.loads(st_profile.read_text(encoding="utf-8"))
    if profile.get("id") != "st-68000-1m-192k-us":
        fail("ST target does not point to canonical M2 profile")

    print("target-matrix: PASS")
    print("targets:", ", ".join(ids))


if __name__ == "__main__":
    main()
