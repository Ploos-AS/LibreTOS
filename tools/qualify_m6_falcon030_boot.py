#!/usr/bin/env python3
"""Run M6.2 Hatari boot regression for canonical Atari Falcon030."""
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
PROFILE = ROOT / "config/m6-falcon030-68030.json"
ROM = ROOT / "build/m6/falcon030/LibreTOS-Falcon030-68030-512k-us.img"
OUT = ROOT / "build/m6/falcon030-boot"
# Hatari can emit host-environment ERROR lines that are non-fatal even when the
# requested guest run completes successfully (notably SDL microphone setup on
# headless GitHub runners). Treat TOS/ROM load failures and FATAL lines as boot
# failures; process exit status remains the primary runtime failure signal.
FATAL = re.compile(r"^FATAL\s*:|cannot load.*tos|invalid.*tos|cannot load.*rom|invalid.*rom", re.I | re.M)
TIMEOUT = int(os.environ.get("HATARI_TIMEOUT_SECONDS", "60"))


def yesno(value: bool) -> str:
    return "yes" if value else "no"


def fail(message: str) -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "RESULT.txt").write_text(
        f"M6.2 Falcon030 boot qualification: FAIL\nreason={message}\n", encoding="utf-8"
    )
    print(f"M6.2 Falcon030 boot qualification: FAIL ({message})", file=sys.stderr)
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
        return fail("canonical Falcon030 profile missing")
    if not ROM.is_file():
        return fail("Falcon030 ROM missing")

    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    machine = profile["machine"]
    qualification = profile["qualification"]

    expected = {
        "id": "falcon030-68030-4m-512k-us",
        "hatari_machine": "falcon",
        "cpu_level": 3,
        "cpu_clock_mhz": 16,
        "st_ram_kib": 4096,
        "fast_ram_kib": 0,
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
        "--machine", "falcon",
        "--memsize", "4",
        "--cpulevel", "3",
        "--cpuclock", "16",
        "--addr24", "no",
        "--mmu", "on",
        "--compatible", yesno(bool(qualification["compatible_mode"])),
        "--fast-boot", yesno(bool(qualification["fast_boot"])),
        "--sound", "off",
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
            "machine=falcon",
            "cpu_level=3",
            "cpu_clock_mhz=16",
            "st_ram_mib=4",
            "fast_ram_mib=0",
            "addressing_bits=32",
            "mmu=on",
            "fpu=optional-not-required",
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
        return fail("fatal TOS/ROM marker in Hatari log")

    result = {
        "schema": 1,
        "milestone": "M6.2",
        "status": "PASS",
        "profile": profile["id"],
        "artifact": ROM.name,
        "sha256": digest,
        "hatari": {
            "machine": "falcon",
            "cpu_level": 3,
            "cpu_clock_mhz": 16,
            "st_ram_mib": 4,
            "fast_ram_mib": 0,
            "addressing_bits": 32,
            "mmu": True,
            "fpu_required": False,
        },
    }
    (OUT / "RESULT.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (OUT / "RESULT.txt").write_text(
        "M6.2 Falcon030 boot qualification: PASS\n"
        f"profile_id={profile['id']}\n"
        f"artifact={ROM.name}\n"
        f"rom_sha256={digest}\n",
        encoding="utf-8",
    )
    print(f"M6.2 Falcon030 boot qualification: PASS ({profile['id']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
