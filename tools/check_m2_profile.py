#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "config" / "m2-st-68000.json"

required = {
    "schema": 1,
    "id": "st-68000-1m-192k-us",
    "milestone": "M2",
}

with PROFILE.open("r", encoding="utf-8") as f:
    data = json.load(f)

for key, value in required.items():
    assert data.get(key) == value, f"{key}: expected {value!r}, got {data.get(key)!r}"

machine = data["machine"]
assert machine["family"] == "Atari ST"
assert machine["hatari_machine"] == "st"
assert machine["cpu"] == "68000"
assert machine["cpu_level"] == 0
assert machine["cpu_clock_mhz"] == 8
assert machine["st_ram_kib"] == 1024
assert machine["fast_ram_kib"] == 0

rom = data["rom"]
assert rom["size_kib"] == 192
assert rom["country"] == "us"

storage = data["storage"]
assert storage["boot_device"] == "rom"
assert storage["hard_disk_required"] is False

q = data["qualification"]
assert q["emulator"] == "Hatari"
assert q["compatible_mode"] is True
assert q["fast_boot"] is False
assert q["minimum_vbls"] >= 500
assert q["proprietary_atari_rom_required"] is False

print(f"M2 ST/68000 profile: PASS ({data['id']})")
