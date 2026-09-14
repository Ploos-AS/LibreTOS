#!/usr/bin/env python3
"""Run the M2.2 Hatari boot regression from the canonical machine profile."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
PROFILE = Path(os.environ.get("PROFILE", ROOT / "config/m2-st-68000.json"))
ROM = Path(os.environ.get("ROM", ROOT / "build/m1/libretos-m1-st-us.img"))
OUT = Path(os.environ.get("OUT", ROOT / "build/m2/boot"))
LOG = OUT / "hatari.log"

FATAL = re.compile(r"fatal|cannot load.*tos|invalid.*tos|bus error|address error", re.I)


def yesno(value: bool) -> str:
    return "yes" if value else "no"


def fail(message: str, rc: int = 1) -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "RESULT.txt").write_text(f"M2.2 boot regression: FAIL\nreason={message}\n", encoding="utf-8")
    print(f"M2.2 boot regression: FAIL ({message})", file=sys.stderr)
    return rc


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

    args = [
        "hatari",
        "--tos", str(ROM),
        "--machine", str(machine["hatari_machine"]),
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
    normalized = json.dumps(profile, indent=2, sort_keys=True) + "\n"
    (OUT / "PROFILE.json").write_text(normalized, encoding="utf-8")

    digest = hashlib.sha256(ROM.read_bytes()).hexdigest()
    (OUT / "ROM.sha256").write_text(f"{digest}  {ROM.name}\n", encoding="utf-8")

    evidence_args = [
        f"profile_id={profile['id']}",
        f"machine={machine['hatari_machine']}",
        f"cpu_level={machine['cpu_level']}",
        f"memsize_mib={ram_kib // 1024}",
        f"compatible={yesno(bool(qualification['compatible_mode']))}",
        f"fast_boot={yesno(bool(qualification['fast_boot']))}",
        f"sound={'on' if qualification['sound'] else 'off'}",
        f"run_vbls={qualification['minimum_vbls']}",
    ]
    (OUT / "HATARI_PROFILE.txt").write_text("\n".join(evidence_args) + "\n", encoding="utf-8")

    command = args
    if shutil.which("xvfb-run"):
        command = ["xvfb-run", "-a", *args]

    completed = subprocess.run(command, cwd=ROOT, check=False)
    if completed.returncode:
        return fail(f"Hatari exit {completed.returncode}", completed.returncode)

    log_text = LOG.read_text(encoding="utf-8", errors="replace") if LOG.exists() else ""
    if FATAL.search(log_text):
        return fail("fatal marker in Hatari log")

    result = (
        "M2.2 boot regression: PASS\n"
        f"profile_id={profile['id']}\n"
        f"rom_sha256={digest}\n"
        f"run_vbls={qualification['minimum_vbls']}\n"
    )
    (OUT / "RESULT.txt").write_text(result, encoding="utf-8")
    print("M2.2 boot regression: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
