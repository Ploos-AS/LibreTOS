#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "config" / "m5-tt030-68030.json"
TARGETS = ROOT / "config" / "targets.json"


def fail(msg: str) -> None:
    raise SystemExit(f"m5-profile: FAIL: {msg}")


def main() -> None:
    if not PROFILE.is_file():
        fail("canonical TT030 profile missing")

    p = json.loads(PROFILE.read_text(encoding="utf-8"))
    if p.get("schema") != 1:
        fail("schema must be 1")
    if p.get("id") != "tt030-68030-4m-16mtt-512k-us":
        fail("unexpected profile id")

    m = p.get("machine", {})
    expected_machine = {
        "family": "Atari TT030",
        "hatari_machine": "tt",
        "cpu": "68030",
        "cpu_level": 3,
        "cpu_clock_mhz": 32,
        "st_ram_kib": 4096,
        "fast_ram_kib": 16384,
        "addressing_bits": 32,
    }
    for key, value in expected_machine.items():
        if m.get(key) != value:
            fail(f"machine.{key} must be {value!r}")

    rom = p.get("rom", {})
    if rom.get("size_kib") != 512 or rom.get("country") != "us":
        fail("ROM contract mismatch")
    if rom.get("source") != "pinned-free-baseline":
        fail("ROM must use free pinned baseline")

    features = p.get("platform_features", {})
    for key in (
        "tt_video", "tt_ram", "mmu", "fpu", "second_mfp", "scc",
        "nvram", "real_time_clock", "scsi", "vme_bus",
    ):
        if features.get(key) is not True:
            fail(f"platform feature {key} must be true")

    q = p.get("qualification", {})
    if q.get("emulator") != "Hatari":
        fail("Hatari must be the qualification emulator")
    if q.get("proprietary_atari_rom_required") is not False:
        fail("qualification must not require proprietary Atari ROM")
    if q.get("must_regress") != [
        "st-68000-1m-192k-us",
        "ste-68000-1m-256k-us",
        "mega-st-68000-4m-192k-us",
        "mega-ste-68000-4m-256k-us",
    ]:
        fail("regression gate mismatch")

    registry = json.loads(TARGETS.read_text(encoding="utf-8"))
    t = next((x for x in registry.get("targets", []) if x.get("id") == "tt030-68030"), None)
    if t is None:
        fail("TT030 target missing from registry")
    if t.get("profile") != "config/m5-tt030-68030.json":
        fail("registry profile mismatch")
    if t.get("cpu") != "68030" or t.get("rom_kib") != 512:
        fail("registry CPU/ROM contract mismatch")
    if t.get("artifact") != "LibreTOS-TT030-68030-512k-us.img":
        fail("registry artifact mismatch")

    print("m5-profile: PASS")
    print(f"profile: {p['id']}")


if __name__ == "__main__":
    main()
