#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "config" / "m3-ste-68000.json"
TARGETS = ROOT / "config" / "targets.json"


def fail(msg: str) -> None:
    raise SystemExit(f"m3-profile: FAIL: {msg}")


def main() -> None:
    p = json.loads(PROFILE.read_text(encoding="utf-8"))
    if p.get("schema") != 1:
        fail("schema must be 1")
    if p.get("id") != "ste-68000-1m-256k-us":
        fail("unexpected profile id")
    m = p.get("machine", {})
    expected_machine = {
        "family": "Atari STe",
        "hatari_machine": "ste",
        "cpu": "68000",
        "cpu_level": 0,
        "cpu_clock_mhz": 8,
        "st_ram_kib": 1024,
        "fast_ram_kib": 0,
    }
    for key, value in expected_machine.items():
        if m.get(key) != value:
            fail(f"machine.{key} must be {value!r}")
    if m.get("representative_models") != ["520STe", "1040STe"]:
        fail("representative STe models mismatch")

    rom = p.get("rom", {})
    if rom.get("size_kib") != 256 or rom.get("country") != "us":
        fail("ROM contract mismatch")
    if rom.get("source") != "pinned-free-baseline":
        fail("ROM must use free pinned baseline")

    features = p.get("platform_features", {})
    for key in ("ste_enhanced_shifter", "dma_sound", "blitter", "hardware_scrolling"):
        if features.get(key) is not True:
            fail(f"platform feature {key} must be enabled")

    q = p.get("qualification", {})
    if q.get("emulator") != "Hatari" or q.get("proprietary_atari_rom_required") is not False:
        fail("qualification contract mismatch")
    if q.get("must_regress") != ["st-68000-1m-192k-us"]:
        fail("ST regression gate missing")

    registry = json.loads(TARGETS.read_text(encoding="utf-8"))
    ste = next((t for t in registry.get("targets", []) if t.get("id") == "ste-68000"), None)
    if ste is None:
        fail("ste-68000 target missing from registry")
    if ste.get("profile") != "config/m3-ste-68000.json":
        fail("registry points to wrong STe profile")
    if ste.get("rom_kib") != 256:
        fail("registry STe ROM size mismatch")
    if ste.get("artifact") != "LibreTOS-STe-68000-256k-us.img":
        fail("registry STe artifact mismatch")
    if ste.get("status") not in {"implemented", "qualified"}:
        fail("STe target must be implemented or qualified")

    print("m3-profile: PASS")
    print("profile:", p["id"])
    print("artifact:", ste["artifact"])


if __name__ == "__main__":
    main()
