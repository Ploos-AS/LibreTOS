#!/usr/bin/env python3
"""Run M5.3 guest-side platform qualification for canonical Atari TT030."""
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
SOURCE = ROOT / "tests/m5/tt030_platform_probe.c"
OUT = ROOT / "build/m5/tt030-platform"
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
        f"M5.3 TT030 platform qualification: FAIL\nreason={message}\n",
        encoding="utf-8",
    )
    print(f"M5.3 TT030 platform qualification: FAIL ({message})", file=sys.stderr)
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
    machine = profile["machine"]
    qualification = profile["qualification"]
    if profile.get("id") != "tt030-68030-4m-16mtt-512k-us":
        return fail("unexpected profile id")

    hd = OUT / "hd"
    probe = hd / "M5TT.TOS"
    result = hd / "M5TT.TXT"
    log = OUT / "hatari.log"
    OUT.mkdir(parents=True, exist_ok=True)
    hd.mkdir(parents=True, exist_ok=True)
    result.unlink(missing_ok=True)

    compile_cmd = [
        "m68k-atari-mint-gcc", "-m68020-60", "-O2", "-s",
        f'-DPROFILE_NAME="{profile["id"]}"',
        '-DRESULT_FILE="C:\\\\M5TT.TXT"',
        "-o", str(probe), str(SOURCE),
    ]
    cp = subprocess.run(compile_cmd, cwd=ROOT, check=False)
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
        "run_vbls": run_vbls,
        "guest_program": "C:\\M5TT.TOS",
        "result_file": "C:\\M5TT.TXT",
        "timeout_seconds": TIMEOUT,
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
        "--sound", "on" if qualification["sound"] else "off",
        "--confirm-quit", "no",
        "--benchmark",
        "--run-vbls", str(run_vbls),
        "--harddrive", str(hd),
        "--protect-hd", "off",
        "--gemdos-case", "upper",
        "--auto", "C:\\M5TT.TOS",
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
        mch = int(fields.get("mch", "-1"), 0)
        cpu = int(fields.get("cpu", "-1"), 0)
        ramtop = int(fields.get("ramtop", "0"), 0)
        rez = int(fields.get("getrez", "-1"), 0)
        phys = int(fields.get("physbase", "0"), 0)
        logbase = int(fields.get("logbase", "0"), 0)
    except ValueError as exc:
        return fail(f"invalid numeric guest field: {exc}")

    if ((mch >> 16) & 0xFFFF) != 2:
        return fail(f"_MCH is not TT family: 0x{mch:08x}")
    if cpu != 30:
        return fail(f"_CPU does not report 68030: {cpu}")
    if ramtop <= 0x01000000:
        return fail(f"TT-RAM top not reported: 0x{ramtop:08x}")
    if rez != 0:
        return fail(f"expected canonical ST-low Getrez=0, got {rez}")
    if phys == 0 or logbase == 0 or (phys & 1) or (logbase & 1):
        return fail("invalid screen base")

    normalized = "\n".join(f"{key}={fields[key]}" for key in sorted(fields)) + "\n"
    (OUT / "GUEST_RESULT.txt").write_text(normalized, encoding="utf-8")
    summary = {
        "schema": 1,
        "milestone": "M5.3",
        "status": "PASS",
        "profile": profile["id"],
        "mch": f"0x{mch:08x}",
        "cpu": cpu,
        "ramtop": f"0x{ramtop:08x}",
        "getrez": rez,
        "physbase": f"0x{phys:08x}",
        "logbase": f"0x{logbase:08x}",
    }
    (OUT / "RESULT.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT / "RESULT.txt").write_text(
        "M5.3 TT030 platform qualification: PASS\n"
        f"profile_id={profile['id']}\n"
        f"mch=0x{mch:08x}\n"
        f"cpu={cpu}\n"
        f"ramtop=0x{ramtop:08x}\n",
        encoding="utf-8",
    )
    print("M5.3 TT030 platform qualification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
