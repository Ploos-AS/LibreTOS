#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "config" / "m2-st-68000.json"
ROM = ROOT / "build" / "m1" / "libretos-m1-st-us.img"
SOURCE = ROOT / "tests" / "m2" / "media_probe.c"
OUT = ROOT / "build" / "m2" / "media"
HD = OUT / "hd"
PROBE = HD / "MEDIA.TOS"
RESULT = HD / "M2MEDIA.TXT"
LOG_A = OUT / "hatari-a.log"
LOG_B = OUT / "hatari-b.log"
DISK_A = OUT / "media-a.st"
DISK_B = OUT / "media-b.st"

FATAL_MARKERS = ("fatal", "cannot load", "invalid tos", "bus error", "address error")


def yn(value: bool) -> str:
    return "yes" if value else "no"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def fail(message: str, log: Path | None = None) -> None:
    print(f"M2.5 floppy/media regression: FAIL ({message})", file=sys.stderr)
    if log and log.exists():
        print(log.read_text(encoding="utf-8", errors="replace"), file=sys.stderr)
    raise SystemExit(1)


def set_fat12_entry(fat: bytearray, cluster: int, value: int) -> None:
    offset = cluster + cluster // 2
    value &= 0xFFF
    if cluster & 1:
        fat[offset] = (fat[offset] & 0x0F) | ((value << 4) & 0xF0)
        fat[offset + 1] = (value >> 4) & 0xFF
    else:
        fat[offset] = value & 0xFF
        fat[offset + 1] = (fat[offset + 1] & 0xF0) | ((value >> 8) & 0x0F)


def make_floppy(path: Path, marker: str) -> None:
    bps = 512
    total_sectors = 1440
    sectors_per_cluster = 2
    reserved = 1
    fats = 2
    root_entries = 112
    sectors_per_fat = 3
    root_sectors = (root_entries * 32 + bps - 1) // bps
    first_data_sector = reserved + fats * sectors_per_fat + root_sectors

    image = bytearray(total_sectors * bps)
    boot = memoryview(image)[:bps]
    boot[0:3] = b"\xEB\x3C\x90"
    boot[3:11] = b"LIBRETOS"
    struct.pack_into("<H", boot, 11, bps)
    boot[13] = sectors_per_cluster
    struct.pack_into("<H", boot, 14, reserved)
    boot[16] = fats
    struct.pack_into("<H", boot, 17, root_entries)
    struct.pack_into("<H", boot, 19, total_sectors)
    boot[21] = 0xF9
    struct.pack_into("<H", boot, 22, sectors_per_fat)
    struct.pack_into("<H", boot, 24, 9)
    struct.pack_into("<H", boot, 26, 2)
    boot[510:512] = b"\x55\xAA"

    fat_size = sectors_per_fat * bps
    fat = bytearray(fat_size)
    fat[0:3] = b"\xF9\xFF\xFF"
    set_fat12_entry(fat, 2, 0xFFF)
    for n in range(fats):
        start = (reserved + n * sectors_per_fat) * bps
        image[start:start + fat_size] = fat

    payload = (f"LibreTOS M2.5 {marker}\r\n").encode("ascii")
    root_start = (reserved + fats * sectors_per_fat) * bps
    entry = bytearray(32)
    entry[0:11] = b"FIXTURE TXT"
    entry[11] = 0x20
    struct.pack_into("<H", entry, 26, 2)
    struct.pack_into("<I", entry, 28, len(payload))
    image[root_start:root_start + 32] = entry

    data_start = first_data_sector * bps
    image[data_start:data_start + len(payload)] = payload
    path.write_bytes(image)


def parse_result(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="ascii", errors="replace").replace("\r\n", "\n")
    fields: dict[str, str] = {}
    for line in text.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            fields[key.strip()] = value.strip()
    return fields


def main() -> None:
    for path, label in ((PROFILE, "profile"), (ROM, "ROM"), (SOURCE, "guest probe source")):
        if not path.is_file():
            fail(f"{label} missing")
    if shutil.which("m68k-atari-mint-gcc") is None:
        fail("m68k-atari-mint-gcc missing")
    if shutil.which("hatari") is None:
        fail("Hatari missing")

    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    machine = profile["machine"]
    q = profile["qualification"]
    ram_kib = int(machine["st_ram_kib"])
    if ram_kib % 1024 != 0:
        fail("ST-RAM must be an integer MiB for this Hatari profile")
    ram_mib = ram_kib // 1024
    run_vbls = max(int(q["minimum_vbls"]), 1800)

    OUT.mkdir(parents=True, exist_ok=True)
    HD.mkdir(parents=True, exist_ok=True)
    RESULT.unlink(missing_ok=True)

    cp = subprocess.run([
        "m68k-atari-mint-gcc", "-m68000", "-O2", "-s",
        "-o", str(PROBE), str(SOURCE)
    ], cwd=ROOT)
    if cp.returncode != 0:
        fail(f"guest probe compile exit {cp.returncode}")

    make_floppy(DISK_A, "MEDIA-A")
    make_floppy(DISK_B, "MEDIA-B")
    initial_hashes = {"MEDIA-A": sha256(DISK_A), "MEDIA-B": sha256(DISK_B)}

    (OUT / "PROBE.sha256").write_text(f"{sha256(PROBE)}  MEDIA.TOS\n", encoding="utf-8")
    (OUT / "ROM.sha256").write_text(f"{sha256(ROM)}  {ROM.name}\n", encoding="utf-8")
    (OUT / "PROFILE.json").write_text(json.dumps(profile, sort_keys=True, indent=2) + "\n", encoding="utf-8")

    effective = {
        "profile_id": profile["id"],
        "machine": machine["hatari_machine"],
        "cpu_level": machine["cpu_level"],
        "st_ram_mib": ram_mib,
        "run_vbls": run_vbls,
        "guest_program": r"C:\MEDIA.TOS",
        "result_file": r"C:\M2MEDIA.TXT",
        "floppy_geometry": "720KiB FAT12, 80x2x9",
        "media_sequence": ["MEDIA-A", "MEDIA-B"],
        "write_protection": "off",
    }
    (OUT / "HATARI_PROFILE.json").write_text(json.dumps(effective, sort_keys=True, indent=2) + "\n", encoding="utf-8")

    runner = ["xvfb-run", "-a"] if shutil.which("xvfb-run") else []
    results = []
    for marker, disk, log in (("MEDIA-A", DISK_A, LOG_A), ("MEDIA-B", DISK_B, LOG_B)):
        RESULT.unlink(missing_ok=True)
        cmd = [
            "hatari",
            "--tos", str(ROM),
            "--machine", str(machine["hatari_machine"]),
            "--memsize", str(ram_mib),
            "--cpulevel", str(machine["cpu_level"]),
            "--compatible", yn(bool(q["compatible_mode"])),
            "--fast-boot", yn(bool(q["fast_boot"])),
            "--sound", "on" if q["sound"] else "off",
            "--confirm-quit", "no",
            "--benchmark",
            "--run-vbls", str(run_vbls),
            "--disk-a", str(disk),
            "--protect-floppy", "off",
            "--harddrive", str(HD),
            "--protect-hd", "off",
            "--gemdos-case", "upper",
            "--auto", r"C:\MEDIA.TOS",
            "--log-file", str(log),
        ]
        cp = subprocess.run(runner + cmd, cwd=ROOT)
        if cp.returncode != 0:
            fail(f"Hatari exit {cp.returncode} for {marker}", log)
        lowered = log.read_text(encoding="utf-8", errors="replace").lower() if log.exists() else ""
        for fatal in FATAL_MARKERS:
            if fatal in lowered:
                fail(f"fatal marker {fatal} for {marker}", log)
        if not RESULT.is_file():
            fail(f"guest result missing for {marker}", log)
        fields = parse_result(RESULT)
        if fields.get("schema") != "1" or fields.get("profile") != profile["id"]:
            fail(f"guest metadata mismatch for {marker}", log)
        if fields.get("status") != "PASS" or fields.get("stage") != "complete":
            fail(f"guest verdict {fields.get('status')} stage={fields.get('stage')} for {marker}", log)
        if fields.get("media_marker") != marker:
            fail(f"media marker mismatch: expected {marker}, got {fields.get('media_marker')}", log)
        final_hash = sha256(disk)
        if final_hash == initial_hashes[marker]:
            fail(f"floppy image did not change after guest write for {marker}", log)
        results.append({
            "marker": marker,
            "initial_sha256": initial_hashes[marker],
            "final_sha256": final_hash,
            "guest_status": fields.get("status"),
            "stage": fields.get("stage"),
        })

    (OUT / "RESULT.json").write_text(json.dumps({"schema": 1, "status": "PASS", "media": results}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT / "DISKS.sha256").write_text(
        f"{sha256(DISK_A)}  {DISK_A.name}\n{sha256(DISK_B)}  {DISK_B.name}\n",
        encoding="utf-8",
    )
    print(f"M2.5 floppy/media regression: PASS ({profile['id']})")


if __name__ == "__main__":
    main()
