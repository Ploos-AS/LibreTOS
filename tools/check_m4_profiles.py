#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = ROOT / "config" / "targets.json"
PROFILES = {
    "mega-st-68000": ROOT / "config" / "m4-mega-st-68000.json",
    "mega-ste-68000": ROOT / "config" / "m4-mega-ste-68000.json",
}


def fail(msg: str) -> None:
    raise SystemExit(f"m4-profiles: FAIL: {msg}")


def check_profile(target_id: str, expected: dict, registry: dict) -> None:
    path = PROFILES[target_id]
    if not path.is_file():
        fail(f"missing profile {path.relative_to(ROOT)}")
    p = json.loads(path.read_text(encoding="utf-8"))
    if p.get("schema") != 1:
        fail(f"{target_id}: schema must be 1")
    if p.get("id") != expected["profile_id"]:
        fail(f"{target_id}: unexpected profile id")
    m = p.get("machine", {})
    for key, value in expected["machine"].items():
        if m.get(key) != value:
            fail(f"{target_id}: machine.{key} must be {value!r}")
    rom = p.get("rom", {})
    if rom.get("size_kib") != expected["rom_kib"] or rom.get("country") != "us":
        fail(f"{target_id}: ROM contract mismatch")
    if rom.get("source") != "pinned-free-baseline":
        fail(f"{target_id}: ROM must use free pinned baseline")
    features = p.get("platform_features", {})
    for key, value in expected["features"].items():
        if features.get(key) is not value:
            fail(f"{target_id}: platform feature {key} must be {value}")
    q = p.get("qualification", {})
    if q.get("emulator") != "Hatari" or q.get("proprietary_atari_rom_required") is not False:
        fail(f"{target_id}: qualification contract mismatch")
    if q.get("must_regress") != expected["must_regress"]:
        fail(f"{target_id}: regression gate mismatch")

    t = next((x for x in registry.get("targets", []) if x.get("id") == target_id), None)
    if t is None:
        fail(f"{target_id}: target missing from registry")
    if t.get("profile") != str(path.relative_to(ROOT)):
        fail(f"{target_id}: registry profile mismatch")
    if t.get("rom_kib") != expected["rom_kib"]:
        fail(f"{target_id}: registry ROM size mismatch")
    if t.get("artifact") != expected["artifact"]:
        fail(f"{target_id}: registry artifact mismatch")


def main() -> None:
    registry = json.loads(TARGETS.read_text(encoding="utf-8"))
    check_profile("mega-st-68000", {
        "profile_id": "mega-st-68000-4m-192k-us",
        "rom_kib": 192,
        "artifact": "LibreTOS-MegaST-68000-192k-us.img",
        "machine": {
            "family": "Atari Mega ST", "hatari_machine": "megast",
            "cpu": "68000", "cpu_level": 0, "cpu_clock_mhz": 8,
            "st_ram_kib": 4096, "fast_ram_kib": 0,
        },
        "features": {
            "blitter": True, "real_time_clock": True,
            "ste_enhanced_shifter": False, "dma_sound": False,
            "hardware_scrolling": False,
        },
        "must_regress": ["st-68000-1m-192k-us"],
    }, registry)
    check_profile("mega-ste-68000", {
        "profile_id": "mega-ste-68000-4m-256k-us",
        "rom_kib": 256,
        "artifact": "LibreTOS-MegaSTe-68000-256k-us.img",
        "machine": {
            "family": "Atari Mega STe", "hatari_machine": "megaste",
            "cpu": "68000", "cpu_level": 0, "cpu_clock_mhz": 16,
            "st_ram_kib": 4096, "fast_ram_kib": 0,
        },
        "features": {
            "ste_enhanced_shifter": True, "dma_sound": True,
            "blitter": True, "hardware_scrolling": True,
            "real_time_clock": True, "cpu_16mhz_mode": True,
            "vme_bus": True, "scc": True,
        },
        "must_regress": ["ste-68000-1m-256k-us", "mega-st-68000-4m-192k-us"],
    }, registry)
    print("m4-profiles: PASS")
    print("profiles: mega-st-68000-4m-192k-us, mega-ste-68000-4m-256k-us")


if __name__ == "__main__":
    main()
