#!/usr/bin/env python3
"""Run M5.4 TT030 enhanced hardware/interface qualification."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "config/m5-tt030-68030.json"
ROM = ROOT / "build/m5/tt030/LibreTOS-TT030-68030-512k-us.img"
SOURCE = ROOT / "tests/m5/tt030_enhanced_probe.c"
OUT = ROOT / "build/m5/tt030-enhanced"
TIMEOUT = int(os.environ.get("HATARI_TIMEOUT_SECONDS", "60"))
FATAL = re.compile(r"(?:^|\n)(?:ERROR|FATAL)\s*:|cannot load.*tos|invalid.*tos", re.I)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def yn(value: bool) -> str:
    return "yes" if value else "no"


def run_bounded(command: list[str]) -> int | None:
    proc = subprocess.Popen(command, cwd=ROOT, start_new_session=True)
    try:
        return proc.wait(timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGTERM)
            proc.wait(timeout=5)
        except (ProcessLookupError, subprocess.TimeoutExpired):
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            proc.wait()
        return None


def fail(message: str) -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "RESULT.txt").write_text(
        f"M5.4 TT030 enhanced qualification: FAIL\nreason={message}\n",
        encoding="utf-8",
    )
    print(f"M5.4 TT030 enhanced qualification: FAIL ({message})", file=sys.stderr)
    return 1


def parse_fields(path: Path) -> dict[str, str]:
    fields: dict[str, str] = {}
    raw = path.read_text(encoding="ascii", errors="replace").replace("\r\n", "\n")
    for line in raw.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            fields[key.strip()] = value.strip()
    return fields


def main() -> int:
    for command in ("m68k-atari-mint-gcc", "hatari"):
        if shutil.which(command) is None:
            return fail(f"{command} missing")
    for path, label in ((PROFILE, "profile"), (ROM, "ROM"), (SOURCE, "probe source")):
        if not path.is_file():
            return fail(f"missing {label}: {path}")

    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    qualification = profile["qualification"]
    if profile.get("id") != "tt030-68030-4m-16mtt-512k-us":
        return fail("unexpected profile id")

    hd = OUT / "hd"
    probe = hd / "M5TTE.TOS"
    result = hd / "M5TTE.TXT"
    log = OUT / "hatari.log"
    OUT.mkdir(parents=True, exist_ok=True)
    hd.mkdir(parents=True, exist_ok=True)
    result.unlink(missing_ok=True)

    cp = subprocess.run([
        "m68k-atari-mint-gcc", "-m68020-60", "-O2", "-s",
        f'-DPROFILE_NAME="{profile["id"]}"',
        '-DRESULT_FILE="C:\\\\M5TTE.TXT"',
        "-o", str(probe), str(SOURCE),
    ], cwd=ROOT, check=False)
    if cp.returncode:
        return fail(f"guest probe compile exit {cp.returncode}")

    run_vbls = max(int(qualification["minimum_vbls"]), 1500)
    effective = {
        "profile_id": profile["id"],
        "machine": "tt",
        "cpu_level": 3,
        "cpu_clock_mhz": 32,
        "st_ram_mib": 4,
        "tt_ram_mib": 16,
        "addressing_bits": 32,
        "fpu": "68882",
        "mmu": True,
        "sound_hz": 44100,
        "run_vbls": run_vbls,
        "guest_program": "C:\\M5TTE.TOS",
        "result_file": "C:\\M5TTE.TXT",
        "qualified_interfaces": ["TT video cookie", "FPU cookie", "TT DMA sound cookie", "FRB cookie"],
        "not_claimed": ["VME bus", "complete SCSI behavior", "SCC traffic", "NVRAM persistence"],
    }
    (OUT / "PROFILE.json").write_text(json.dumps(profile, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT / "ROM.sha256").write_text(f"{sha256(ROM)}  {ROM.name}\n", encoding="utf-8")
    (OUT / "PROBE.sha256").write_text(f"{sha256(probe)}  {probe.name}\n", encoding="utf-8")
    (OUT / "HATARI_PROFILE.json").write_text(json.dumps(effective, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    cmd = [
        "hatari",
        "--tos", str(ROM),
        "--machine", "tt",
        "--memsize", "4",
        "--ttram", "16",
        "--cpulevel", "3",
        "--cpuclock", "32",
        "--addr24", "no",
        "--fpu", "68882",
        "--mmu", "on",
        "--compatible", yn(bool(qualification["compatible_mode"])),
        "--fast-boot", yn(bool(qualification["fast_boot"])),
        "--sound", "44100",
        "--confirm-quit", "no",
        "--benchmark",
        "--run-vbls", str(run_vbls),
        "--harddrive", str(hd),
        "--protect-hd", "off",
        "--gemdos-case", "upper",
        "--auto", "C:\\M5TTE.TOS",
        "--log-file", str(log),
    ]
    command = cmd if shutil.which("xvfb-run") is None else ["xvfb-run", "-a", *cmd]
    rc = run_bounded(command)
    if rc is None:
        return fail(f"Hatari timeout after {TIMEOUT}s")
    if rc:
        return fail(f"Hatari exit {rc}")

    log_text = log.read_text(encoding="utf-8", errors="replace") if log.exists() else ""
    if FATAL.search(log_text):
        return fail("fatal marker in Hatari log")
    if not result.is_file():
        return fail("guest result missing")

    fields = parse_fields(result)
    if fields.get("schema") != "1":
        return fail("guest schema mismatch")
    if fields.get("profile") != profile["id"]:
        return fail("guest profile mismatch")
    if fields.get("status") != "PASS":
        return fail(f"guest verdict {fields.get('status', 'missing')} stage={fields.get('stage', 'unknown')}")

    try:
        vdo = int(fields.get("vdo", "-1"), 0)
        fpu = int(fields.get("fpu", "-1"), 0)
        snd = int(fields.get("snd", "-1"), 0)
        frb = int(fields.get("frb", "0"), 0)
    except ValueError as exc:
        return fail(f"invalid numeric guest field: {exc}")

    if vdo != 0x00020000:
        return fail(f"_VDO does not report TT video: 0x{vdo:08x}")
    if fpu < 0:
        return fail("_FPU cookie missing")
    if (snd & 0x03) != 0x03:
        return fail(f"_SND lacks PSG+8-bit DMA bits: 0x{snd:08x}")
    if frb == 0:
        return fail("_FRB cookie missing with TT-RAM enabled")

    normalized = "\n".join(f"{key}={fields[key]}" for key in sorted(fields)) + "\n"
    (OUT / "GUEST_RESULT.txt").write_text(normalized, encoding="utf-8")
    summary = {
        "schema": 1,
        "milestone": "M5.4",
        "status": "PASS",
        "profile": profile["id"],
        "vdo": f"0x{vdo:08x}",
        "fpu": f"0x{fpu:08x}",
        "snd": f"0x{snd:08x}",
        "frb": f"0x{frb:08x}",
        "scope": {
            "qualified": ["TT video identification", "FPU discovery", "TT DMA sound discovery", "TT-RAM FRB presence"],
            "excluded": ["VME", "complete SCSI semantics", "SCC traffic", "NVRAM persistence"],
        },
    }
    (OUT / "RESULT.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT / "RESULT.txt").write_text(
        "M5.4 TT030 enhanced qualification: PASS\n"
        f"profile_id={profile['id']}\n"
        f"vdo=0x{vdo:08x}\n"
        f"fpu=0x{fpu:08x}\n"
        f"snd=0x{snd:08x}\n"
        f"frb=0x{frb:08x}\n",
        encoding="utf-8",
    )
    print("M5.4 TT030 enhanced qualification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
