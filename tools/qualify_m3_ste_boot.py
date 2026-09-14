#!/usr/bin/env python3
"""Run the M3.2 Hatari boot regression for the canonical Atari STe profile."""

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

ROOT = Path(__file__).resolve().parent.parent
PROFILE = ROOT / "config/m3-ste-68000.json"
ROM = ROOT / "build/m3/ste/LibreTOS-STe-68000-256k-us.img"
OUT = ROOT / "build/m3/ste-boot"
LOG = OUT / "hatari.log"
FATAL = re.compile(r"fatal|cannot load.*tos|invalid.*tos|bus error|address error", re.I)
HATARI_TIMEOUT_SECONDS = int(os.environ.get("HATARI_TIMEOUT_SECONDS", "60"))


def yesno(value: bool) -> str:
    return "yes" if value else "no"


def fail(message: str, rc: int = 1) -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "RESULT.txt").write_text(f"M3.2 STe boot regression: FAIL\nreason={message}\n", encoding="utf-8")
    print(f"M3.2 STe boot regression: FAIL ({message})", file=sys.stderr)
    return rc


def run_bounded(command: list[str]) -> tuple[int | None, bool]:
    proc = subprocess.Popen(command, cwd=ROOT, start_new_session=True)
    try:
        return proc.wait(timeout=HATARI_TIMEOUT_SECONDS), False
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
    if not PROFILE.is_file():
        return fail(f"profile not found: {PROFILE}")
    if not ROM.is_file():
        return fail(f"ROM not found: {ROM}")
    if shutil.which("hatari") is None:
        return fail("hatari not found")

    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    machine = profile["machine"]
    qualification = profile["qualification"]
    ram_kib = int(machine["st_ram_kib"])
    if ram_kib % 1024:
        return fail("st_ram_kib must be an integer MiB for Hatari --memsize")
    if machine["hatari_machine"] != "ste":
        return fail("canonical STe profile must use Hatari machine 'ste'")
    if int(profile["rom"]["size_kib"]) != 256:
        return fail("canonical STe profile must use a 256 KiB ROM")

    args = [
        "hatari",
        "--tos", str(ROM),
        "--machine", "ste",
        "--memsize", str(ram_kib // 1024),
        "--cpulevel", str(machine["cpu_level"]),
        "--compatible", yesno(bool(qualification["compatible_mode"])),
        "--fast-boot", yesno(bool(qualification["fast_boot"])),
        "--sound", "on" if qualification["sound"] else "off",
        "--confirm-quit", "no",
        "--benchmark",
        "--run-vbls", str(qualification["minimum_vbls"]),
        "--log-file", str(LOG),
    ]

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "PROFILE.json").write_text(json.dumps(profile, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    digest = hashlib.sha256(ROM.read_bytes()).hexdigest()
    (OUT / "ROM.sha256").write_text(f"{digest}  {ROM.name}\n", encoding="utf-8")
    (OUT / "HATARI_PROFILE.txt").write_text(
        "\n".join([
            f"profile_id={profile['id']}",
            "machine=ste",
            f"cpu_level={machine['cpu_level']}",
            f"memsize_mib={ram_kib // 1024}",
            "rom_kib=256",
            f"compatible={yesno(bool(qualification['compatible_mode']))}",
            f"fast_boot={yesno(bool(qualification['fast_boot']))}",
            f"sound={'on' if qualification['sound'] else 'off'}",
            f"run_vbls={qualification['minimum_vbls']}",
            f"timeout_seconds={HATARI_TIMEOUT_SECONDS}",
        ]) + "\n",
        encoding="utf-8",
    )

    command = args if shutil.which("xvfb-run") is None else ["xvfb-run", "-a", *args]
    returncode, timed_out = run_bounded(command)
    if timed_out:
        return fail(f"Hatari timeout after {HATARI_TIMEOUT_SECONDS}s")
    if returncode:
        return fail(f"Hatari exit {returncode}", int(returncode))

    log_text = LOG.read_text(encoding="utf-8", errors="replace") if LOG.exists() else ""
    if FATAL.search(log_text):
        return fail("fatal marker in Hatari log")

    (OUT / "RESULT.txt").write_text(
        "M3.2 STe boot regression: PASS\n"
        f"profile_id={profile['id']}\n"
        f"artifact={ROM.name}\n"
        f"rom_sha256={digest}\n"
        f"run_vbls={qualification['minimum_vbls']}\n"
        f"timeout_seconds={HATARI_TIMEOUT_SECONDS}\n",
        encoding="utf-8",
    )
    print("M3.2 STe boot regression: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
