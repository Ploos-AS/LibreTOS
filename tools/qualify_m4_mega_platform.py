#!/usr/bin/env python3
"""Run M4.3 guest-side platform qualification for Mega ST and Mega STe."""

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
SOURCE = ROOT / "tests/m4/mega_platform_probe.c"
OUT = ROOT / "build/m4/mega-platform"
TIMEOUT = int(os.environ.get("HATARI_TIMEOUT_SECONDS", "60"))
FATAL = re.compile(r"(?:^|\n)(?:ERROR|FATAL)\s*:|cannot load.*tos|invalid.*tos", re.I)

TARGETS = [
    {
        "name": "Mega ST",
        "slug": "megast",
        "profile": ROOT / "config/m4-mega-st-68000.json",
        "rom": ROOT / "build/m4/mega/LibreTOS-MegaST-68000-192k-us.img",
        "program": "M4MST.TOS",
        "result": "M4MST.TXT",
        "expect_ste": 0,
        "expect_dma": 0,
    },
    {
        "name": "Mega STe",
        "slug": "megaste",
        "profile": ROOT / "config/m4-mega-ste-68000.json",
        "rom": ROOT / "build/m4/mega/LibreTOS-MegaSTe-68000-256k-us.img",
        "program": "M4MSTE.TOS",
        "result": "M4MSTE.TXT",
        "expect_ste": 1,
        "expect_dma": 1,
    },
]


def yn(value: bool) -> str:
    return "yes" if value else "no"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


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
        f"M4.3 Mega platform qualification: FAIL\nreason={message}\n",
        encoding="utf-8",
    )
    print(f"M4.3 Mega platform qualification: FAIL ({message})", file=sys.stderr)
    return 1


def parse_fields(path: Path) -> dict[str, str]:
    fields: dict[str, str] = {}
    raw = path.read_text(encoding="ascii", errors="replace").replace("\r\n", "\n")
    for line in raw.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            fields[key.strip()] = value.strip()
    return fields


def qualify(target: dict[str, object]) -> dict[str, object]:
    name = str(target["name"])
    slug = str(target["slug"])
    profile_path = Path(target["profile"])
    rom = Path(target["rom"])
    program_name = str(target["program"])
    result_name = str(target["result"])
    expect_ste = int(target["expect_ste"])
    expect_dma = int(target["expect_dma"])

    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    machine = profile["machine"]
    qualification = profile["qualification"]
    if machine["hatari_machine"] != slug:
        raise RuntimeError(f"{name}: Hatari machine mismatch")

    target_out = OUT / slug
    hd = target_out / "hd"
    probe = hd / program_name
    result = hd / result_name
    log = target_out / "hatari.log"
    target_out.mkdir(parents=True, exist_ok=True)
    hd.mkdir(parents=True, exist_ok=True)
    result.unlink(missing_ok=True)

    guest_result = f"C:\\{result_name}"
    escaped_result = guest_result.replace("\\", "\\\\")
    compile_cmd = [
        "m68k-atari-mint-gcc", "-m68000", "-O2", "-s",
        f'-DPROFILE_NAME="{profile["id"]}"',
        f'-DRESULT_FILE="{escaped_result}"',
        f"-DEXPECT_STE_FAMILY={expect_ste}",
        f"-DEXPECT_DMA_SOUND={expect_dma}",
        "-o", str(probe), str(SOURCE),
    ]
    cp = subprocess.run(compile_cmd, cwd=ROOT, check=False)
    if cp.returncode:
        raise RuntimeError(f"{name}: guest probe compile exit {cp.returncode}")

    ram_kib = int(machine["st_ram_kib"])
    if ram_kib % 1024:
        raise RuntimeError(f"{name}: ST-RAM must be integer MiB")
    ram_mib = ram_kib // 1024
    run_vbls = max(int(qualification["minimum_vbls"]), 1500)

    effective = {
        "profile_id": profile["id"],
        "machine": slug,
        "cpu_level": machine["cpu_level"],
        "cpu_clock_mhz": machine["cpu_clock_mhz"],
        "st_ram_mib": ram_mib,
        "run_vbls": run_vbls,
        "timeout_seconds": TIMEOUT,
        "guest_program": f"C:\\{program_name}",
        "result_file": guest_result,
        "expect_ste_family": bool(expect_ste),
        "expect_dma_sound": bool(expect_dma),
    }
    (target_out / "PROFILE.json").write_text(json.dumps(profile, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (target_out / "ROM.sha256").write_text(f"{sha256(rom)}  {rom.name}\n", encoding="utf-8")
    (target_out / "PROBE.sha256").write_text(f"{sha256(probe)}  {probe.name}\n", encoding="utf-8")
    (target_out / "HATARI_PROFILE.json").write_text(json.dumps(effective, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    cmd = [
        "hatari",
        "--tos", str(rom),
        "--machine", slug,
        "--memsize", str(ram_mib),
        "--cpulevel", str(machine["cpu_level"]),
        "--compatible", yn(bool(qualification["compatible_mode"])),
        "--fast-boot", yn(bool(qualification["fast_boot"])),
        "--sound", "on" if qualification["sound"] else "off",
        "--confirm-quit", "no",
        "--benchmark",
        "--run-vbls", str(run_vbls),
        "--harddrive", str(hd),
        "--protect-hd", "off",
        "--gemdos-case", "upper",
        "--auto", f"C:\\{program_name}",
        "--log-file", str(log),
    ]
    command = cmd if shutil.which("xvfb-run") is None else ["xvfb-run", "-a", *cmd]
    rc = run_bounded(command)
    if rc is None:
        raise RuntimeError(f"{name}: Hatari timeout after {TIMEOUT}s")
    if rc:
        raise RuntimeError(f"{name}: Hatari exit {rc}")

    log_text = log.read_text(encoding="utf-8", errors="replace") if log.exists() else ""
    if FATAL.search(log_text):
        raise RuntimeError(f"{name}: fatal marker in Hatari log")
    if not result.is_file():
        raise RuntimeError(f"{name}: guest result missing")

    fields = parse_fields(result)
    if fields.get("schema") != "1":
        raise RuntimeError(f"{name}: guest schema mismatch")
    if fields.get("profile") != profile["id"]:
        raise RuntimeError(f"{name}: guest profile mismatch")
    if fields.get("status") != "PASS":
        raise RuntimeError(f"{name}: guest verdict {fields.get('status', 'missing')} stage={fields.get('stage', 'unknown')}")

    mch = int(fields.get("mch", "-1"), 0)
    snd = int(fields.get("snd", "-1"), 0)
    rez = int(fields.get("getrez", "-1"), 0)
    blit = int(fields.get("blitmode", "0"), 0)
    family = (mch >> 16) & 0xffff

    if expect_ste and family != 1:
        raise RuntimeError(f"{name}: _MCH family mismatch 0x{mch:08x}")
    if not expect_ste and family == 1:
        raise RuntimeError(f"{name}: unexpectedly reports STe family 0x{mch:08x}")
    if expect_dma and (snd & 0x3) != 0x3:
        raise RuntimeError(f"{name}: _SND lacks PSG+DMA bits 0x{snd:08x}")
    if not expect_dma and (snd & 0x2):
        raise RuntimeError(f"{name}: unexpected DMA sound bit 0x{snd:08x}")
    if rez != 0:
        raise RuntimeError(f"{name}: expected ST-low Getrez=0, got {rez}")
    if (blit & 0x2) == 0:
        raise RuntimeError(f"{name}: blitter not reported 0x{blit:04x}")

    normalized = "\n".join(f"{key}={fields[key]}" for key in sorted(fields)) + "\n"
    (target_out / "RESULT.txt").write_text(normalized, encoding="utf-8")
    return {
        "name": name,
        "profile_id": profile["id"],
        "mch": f"0x{mch:08x}",
        "snd": f"0x{snd:08x}",
        "blitmode": f"0x{blit:04x}",
        "status": "PASS",
    }


def main() -> int:
    for command in ("m68k-atari-mint-gcc", "hatari"):
        if shutil.which(command) is None:
            return fail(f"{command} missing")
    if not SOURCE.is_file():
        return fail(f"guest probe source missing: {SOURCE}")

    results = []
    try:
        for target in TARGETS:
            results.append(qualify(target))
    except (OSError, RuntimeError, ValueError, KeyError) as exc:
        return fail(str(exc))

    (OUT / "RESULT.json").write_text(
        json.dumps({"schema": 1, "milestone": "M4.3", "status": "PASS", "targets": results}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (OUT / "RESULT.txt").write_text(
        "M4.3 Mega platform qualification: PASS\n"
        "targets=Mega ST,Mega STe\n",
        encoding="utf-8",
    )
    print("M4.3 Mega platform qualification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
