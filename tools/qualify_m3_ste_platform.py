#!/usr/bin/env python3
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
PROFILE = ROOT / "config" / "m3-ste-68000.json"
ROM = ROOT / "build" / "m3" / "ste" / "LibreTOS-STe-68000-256k-us.img"
SOURCE = ROOT / "tests" / "m3" / "ste_platform_probe.c"
OUT = ROOT / "build" / "m3" / "ste-platform"
HD = OUT / "hd"
PROBE = HD / "STEPLAT.TOS"
RESULT = HD / "M3STE.TXT"
LOG = OUT / "hatari.log"
TIMEOUT = int(os.environ.get("HATARI_TIMEOUT_SECONDS", "60"))
FATAL = re.compile(r"(?:^|\n)(?:ERROR|FATAL)\s*:|cannot load.*tos|invalid.*tos", re.I)


def yn(value: bool) -> str:
    return "yes" if value else "no"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def fail(message: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "RESULT.txt").write_text(
        f"M3.3 STe platform qualification: FAIL\nreason={message}\n",
        encoding="utf-8",
    )
    print(f"M3.3 STe platform qualification: FAIL ({message})", file=sys.stderr)
    raise SystemExit(1)


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


def main() -> None:
    for path, label in ((PROFILE, "profile"), (ROM, "ROM"), (SOURCE, "guest probe source")):
        if not path.is_file():
            fail(f"{label} missing: {path}")
    if shutil.which("m68k-atari-mint-gcc") is None:
        fail("m68k-atari-mint-gcc missing")
    if shutil.which("hatari") is None:
        fail("Hatari missing")

    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    machine = profile["machine"]
    q = profile["qualification"]
    if profile["id"] != "ste-68000-1m-256k-us":
        fail("unexpected STe profile id")
    if machine["hatari_machine"] != "ste":
        fail("canonical STe profile must use Hatari machine ste")

    ram_kib = int(machine["st_ram_kib"])
    if ram_kib % 1024:
        fail("ST-RAM must be an integer MiB")
    ram_mib = ram_kib // 1024
    run_vbls = max(int(q["minimum_vbls"]), 1500)

    OUT.mkdir(parents=True, exist_ok=True)
    HD.mkdir(parents=True, exist_ok=True)
    RESULT.unlink(missing_ok=True)

    compile_cmd = [
        "m68k-atari-mint-gcc", "-m68000", "-O2", "-s",
        "-o", str(PROBE), str(SOURCE),
    ]
    cp = subprocess.run(compile_cmd, cwd=ROOT, check=False)
    if cp.returncode:
        fail(f"guest probe compile exit {cp.returncode}")

    (OUT / "PROFILE.json").write_text(json.dumps(profile, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT / "ROM.sha256").write_text(f"{sha256(ROM)}  {ROM.name}\n", encoding="utf-8")
    (OUT / "PROBE.sha256").write_text(f"{sha256(PROBE)}  {PROBE.name}\n", encoding="utf-8")

    effective = {
        "profile_id": profile["id"],
        "machine": "ste",
        "cpu_level": machine["cpu_level"],
        "st_ram_mib": ram_mib,
        "run_vbls": run_vbls,
        "timeout_seconds": TIMEOUT,
        "guest_program": r"C:\STEPLAT.TOS",
        "result_file": r"C:\M3STE.TXT",
    }
    (OUT / "HATARI_PROFILE.json").write_text(json.dumps(effective, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    cmd = [
        "hatari",
        "--tos", str(ROM),
        "--machine", "ste",
        "--memsize", str(ram_mib),
        "--cpulevel", str(machine["cpu_level"]),
        "--compatible", yn(bool(q["compatible_mode"])),
        "--fast-boot", yn(bool(q["fast_boot"])),
        "--sound", "on" if q["sound"] else "off",
        "--confirm-quit", "no",
        "--benchmark",
        "--run-vbls", str(run_vbls),
        "--harddrive", str(HD),
        "--protect-hd", "off",
        "--gemdos-case", "upper",
        "--auto", r"C:\STEPLAT.TOS",
        "--log-file", str(LOG),
    ]
    command = cmd if shutil.which("xvfb-run") is None else ["xvfb-run", "-a", *cmd]
    rc = run_bounded(command)
    if rc is None:
        fail(f"Hatari timeout after {TIMEOUT}s")
    if rc:
        fail(f"Hatari exit {rc}")

    log_text = LOG.read_text(encoding="utf-8", errors="replace") if LOG.exists() else ""
    if FATAL.search(log_text):
        fail("fatal marker in Hatari log")
    if not RESULT.is_file():
        fail("guest result missing")

    raw = RESULT.read_text(encoding="ascii", errors="replace").replace("\r\n", "\n")
    fields: dict[str, str] = {}
    for line in raw.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            fields[key.strip()] = value.strip()

    if fields.get("schema") != "1":
        fail("guest result schema mismatch")
    if fields.get("profile") != profile["id"]:
        fail("guest result profile mismatch")
    if fields.get("status") != "PASS":
        fail(f"guest verdict {fields.get('status', 'missing')} stage={fields.get('stage', 'unknown')}")

    mch = int(fields.get("mch", "-1"), 0)
    snd = int(fields.get("snd", "-1"), 0)
    rez = int(fields.get("getrez", "-1"), 0)
    blit = int(fields.get("blitmode", "0"), 0)

    if (mch >> 16) != 1:
        fail(f"_MCH does not identify STe family: 0x{mch:08x}")
    if (snd & 0x3) != 0x3:
        fail(f"_SND missing PSG+DMA sound bits: 0x{snd:08x}")
    if rez != 0:
        fail(f"Getrez expected ST-low (0), got {rez}")
    if (blit & 0x2) == 0:
        fail(f"Blitmode reports no blitter: 0x{blit:04x}")

    normalized = "\n".join(f"{k}={fields[k]}" for k in sorted(fields)) + "\n"
    (OUT / "RESULT.txt").write_text(normalized, encoding="utf-8")
    print(f"M3.3 STe platform qualification: PASS ({profile['id']})")


if __name__ == "__main__":
    main()
