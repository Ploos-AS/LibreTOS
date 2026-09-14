#!/usr/bin/env python3
"""Run M5.2 Hatari boot regression for canonical Atari TT030."""
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
OUT = ROOT / "build/m5/tt030-boot"
FATAL = re.compile(r"^(?:ERROR|FATAL)\s*:|cannot load.*tos|invalid.*tos", re.I | re.M)
TIMEOUT = int(os.environ.get("HATARI_TIMEOUT_SECONDS", "60"))


def yesno(value: bool) -> str:
    return "yes" if value else "no"


def fail(message: str) -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "RESULT.txt").write_text(
        f"M5.2 TT030 boot qualification: FAIL\nreason={message}\n", encoding="utf-8"
    )
    print(f"M5.2 TT030 boot qualification: FAIL ({message})", file=sys.stderr)
    return 1


def run_bounded(command: list[str]) -> tuple[int | None, bool]:
    proc = subprocess.Popen(command, cwd=ROOT, start_new_session=True)
    try:
        return proc.wait(timeout=TIMEOUT), False
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
        return None, True


def main() -> int:
    if shutil.which("hatari") is None:
        return fail("hatari not found")
    if not PROFILE.is_file():
        return fail("canonical TT030 profile missing")
    if not ROM.is_file():
        return fail("TT030 ROM missing")

    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    machine = profile["machine"]
    qualification = profile["qualification"]

    expected = {
        "id": "tt030-68030-4m-16mtt-512k-us",
        "hatari_machine": "tt",
        "cpu_level": 3,
        "cpu_clock_mhz": 32,
        "st_ram_kib": 4096,
        "fast_ram_kib": 16384,
        "addressing_bits": 32,
        "rom_kib": 512,
    }
    if profile.get("id") != expected["id"]:
        return fail("unexpected profile id")
    for key in ("hatari_machine", "cpu_level", "cpu_clock_mhz", "st_ram_kib", "fast_ram_kib", "addressing_bits"):
        if machine.get(key) != expected[key]:
            return fail(f"machine.{key} contract mismatch")
    if profile["rom"].get("size_kib") != expected["rom_kib"]:
        return fail("ROM size contract mismatch")
    if ROM.stat().st_size != 512 * 1024:
        return fail("ROM artifact byte size mismatch")

    OUT.mkdir(parents=True, exist_ok=True)
    log = OUT / "hatari.log"
    digest = hashlib.sha256(ROM.read_bytes()).hexdigest()

    args = [
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
        "--compatible", yesno(bool(qualification["compatible_mode"])),
        "--fast-boot", yesno(bool(qualification["fast_boot"])),
        "--sound", "on" if qualification["sound"] else "off",
        "--confirm-quit", "no",
        "--benchmark",
        "--run-vbls", str(qualification["minimum_vbls"]),
        "--log-file", str(log),
    ]

    (OUT / "PROFILE.json").write_text(
        json.dumps(profile, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (OUT / "ROM.sha256").write_text(f"{digest}  {ROM.name}\n", encoding="utf-8")
    (OUT / "HATARI_PROFILE.txt").write_text(
        "\n".join([
            f"profile_id={profile['id']}",
            "machine=tt",
            "cpu_level=3",
            "cpu_clock_mhz=32",
            "st_ram_mib=4",
            "tt_ram_mib=16",
            "addressing_bits=32",
            "fpu=68882",
            "mmu=on",
            "rom_kib=512",
            f"compatible={yesno(bool(qualification['compatible_mode']))}",
            f"fast_boot={yesno(bool(qualification['fast_boot']))}",
            f"run_vbls={qualification['minimum_vbls']}",
            f"timeout_seconds={TIMEOUT}",
        ]) + "\n",
        encoding="utf-8",
    )

    command = args if shutil.which("xvfb-run") is None else ["xvfb-run", "-a", *args]
    returncode, timed_out = run_bounded(command)
    if timed_out:
        return fail(f"Hatari timeout after {TIMEOUT}s")
    if returncode:
        return fail(f"Hatari exit {returncode}")

    log_text = log.read_text(encoding="utf-8", errors="replace") if log.exists() else ""
    if FATAL.search(log_text):
        return fail("fatal marker in Hatari log")

    result = {
        "schema": 1,
        "milestone": "M5.2",
        "status": "PASS",
        "profile": profile["id"],
        "artifact": ROM.name,
        "sha256": digest,
        "hatari": {
            "machine": "tt",
            "cpu_level": 3,
            "cpu_clock_mhz": 32,
            "st_ram_mib": 4,
            "tt_ram_mib": 16,
            "addressing_bits": 32,
            "fpu": "68882",
            "mmu": True,
        },
    }
    (OUT / "RESULT.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (OUT / "RESULT.txt").write_text(
        "M5.2 TT030 boot qualification: PASS\n"
        f"profile_id={profile['id']}\n"
        f"artifact={ROM.name}\n"
        f"rom_sha256={digest}\n",
        encoding="utf-8",
    )
    print(f"M5.2 TT030 boot qualification: PASS ({profile['id']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
