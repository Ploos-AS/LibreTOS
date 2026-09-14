#!/usr/bin/env python3
"""Run M4.2 Hatari boot regressions for Mega ST and Mega STe."""

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
OUT = ROOT / "build/m4/mega-boot"
FATAL = re.compile(r"^(?:ERROR|FATAL)\s*:|cannot load.*tos|invalid.*tos", re.I | re.M)
TIMEOUT = int(os.environ.get("HATARI_TIMEOUT_SECONDS", "60"))

TARGETS = [
    {
        "name": "Mega ST",
        "profile": ROOT / "config/m4-mega-st-68000.json",
        "rom": ROOT / "build/m4/mega/LibreTOS-MegaST-68000-192k-us.img",
        "machine": "megast",
        "rom_kib": 192,
    },
    {
        "name": "Mega STe",
        "profile": ROOT / "config/m4-mega-ste-68000.json",
        "rom": ROOT / "build/m4/mega/LibreTOS-MegaSTe-68000-256k-us.img",
        "machine": "megaste",
        "rom_kib": 256,
    },
]


def yesno(value: bool) -> str:
    return "yes" if value else "no"


def fail(message: str) -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "RESULT.txt").write_text(f"M4.2 Mega boot qualification: FAIL\nreason={message}\n", encoding="utf-8")
    print(f"M4.2 Mega boot qualification: FAIL ({message})", file=sys.stderr)
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


def qualify(target: dict[str, object]) -> dict[str, object]:
    profile_path = Path(target["profile"])
    rom = Path(target["rom"])
    machine_name = str(target["machine"])
    rom_kib = int(target["rom_kib"])
    name = str(target["name"])

    if not profile_path.is_file():
        raise RuntimeError(f"{name}: missing profile")
    if not rom.is_file():
        raise RuntimeError(f"{name}: missing ROM")

    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    machine = profile["machine"]
    qualification = profile["qualification"]
    ram_kib = int(machine["st_ram_kib"])

    if machine["hatari_machine"] != machine_name:
        raise RuntimeError(f"{name}: Hatari machine mismatch")
    if int(profile["rom"]["size_kib"]) != rom_kib:
        raise RuntimeError(f"{name}: ROM size contract mismatch")
    if ram_kib % 1024:
        raise RuntimeError(f"{name}: RAM must be integer MiB")
    if rom.stat().st_size != rom_kib * 1024:
        raise RuntimeError(f"{name}: ROM artifact byte size mismatch")

    slug = machine_name
    target_out = OUT / slug
    target_out.mkdir(parents=True, exist_ok=True)
    log = target_out / "hatari.log"
    digest = hashlib.sha256(rom.read_bytes()).hexdigest()

    args = [
        "hatari",
        "--tos", str(rom),
        "--machine", machine_name,
        "--memsize", str(ram_kib // 1024),
        "--cpulevel", str(machine["cpu_level"]),
        "--compatible", yesno(bool(qualification["compatible_mode"])),
        "--fast-boot", yesno(bool(qualification["fast_boot"])),
        "--sound", "on" if qualification["sound"] else "off",
        "--confirm-quit", "no",
        "--benchmark",
        "--run-vbls", str(qualification["minimum_vbls"]),
        "--log-file", str(log),
    ]

    (target_out / "PROFILE.json").write_text(json.dumps(profile, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (target_out / "ROM.sha256").write_text(f"{digest}  {rom.name}\n", encoding="utf-8")
    (target_out / "HATARI_PROFILE.txt").write_text(
        "\n".join([
            f"profile_id={profile['id']}",
            f"machine={machine_name}",
            f"cpu_level={machine['cpu_level']}",
            f"cpu_clock_mhz={machine['cpu_clock_mhz']}",
            f"memsize_mib={ram_kib // 1024}",
            f"rom_kib={rom_kib}",
            f"compatible={yesno(bool(qualification['compatible_mode']))}",
            f"fast_boot={yesno(bool(qualification['fast_boot']))}",
            f"sound={'on' if qualification['sound'] else 'off'}",
            f"run_vbls={qualification['minimum_vbls']}",
            f"timeout_seconds={TIMEOUT}",
        ]) + "\n",
        encoding="utf-8",
    )

    command = args if shutil.which("xvfb-run") is None else ["xvfb-run", "-a", *args]
    returncode, timed_out = run_bounded(command)
    if timed_out:
        raise RuntimeError(f"{name}: Hatari timeout after {TIMEOUT}s")
    if returncode:
        raise RuntimeError(f"{name}: Hatari exit {returncode}")

    log_text = log.read_text(encoding="utf-8", errors="replace") if log.exists() else ""
    if FATAL.search(log_text):
        raise RuntimeError(f"{name}: fatal marker in Hatari log")

    (target_out / "RESULT.txt").write_text(
        f"M4.2 {name} boot regression: PASS\n"
        f"profile_id={profile['id']}\n"
        f"artifact={rom.name}\n"
        f"rom_sha256={digest}\n"
        f"run_vbls={qualification['minimum_vbls']}\n",
        encoding="utf-8",
    )
    return {"name": name, "profile_id": profile["id"], "artifact": rom.name, "sha256": digest}


def main() -> int:
    if shutil.which("hatari") is None:
        return fail("hatari not found")

    OUT.mkdir(parents=True, exist_ok=True)
    results = []
    try:
        for target in TARGETS:
            results.append(qualify(target))
    except RuntimeError as exc:
        return fail(str(exc))

    (OUT / "RESULT.json").write_text(
        json.dumps({"schema": 1, "milestone": "M4.2", "status": "PASS", "targets": results}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (OUT / "RESULT.txt").write_text(
        "M4.2 Mega boot qualification: PASS\n"
        "targets=Mega ST,Mega STe\n",
        encoding="utf-8",
    )
    print("M4.2 Mega boot qualification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
