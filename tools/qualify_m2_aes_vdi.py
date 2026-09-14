#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "config" / "m2-st-68000.json"
ROM = ROOT / "build" / "m1" / "libretos-m1-st-us.img"
SOURCE = ROOT / "tests" / "m2" / "aes_vdi_probe.c"
OUT = ROOT / "build" / "m2" / "aes-vdi"
HD = OUT / "hd"
PROBE = HD / "AESVDI.PRG"
RESULT = HD / "M2AESVD.TXT"
LOG = OUT / "hatari.log"

FATAL_MARKERS = (
    "fatal",
    "cannot load",
    "invalid tos",
    "bus error",
    "address error",
)


def yn(value: bool) -> str:
    return "yes" if value else "no"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def fail(message: str) -> None:
    print(f"M2.4 AES/VDI regression: FAIL ({message})", file=sys.stderr)
    if LOG.exists():
        print(LOG.read_text(encoding="utf-8", errors="replace"), file=sys.stderr)
    raise SystemExit(1)


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
    run_vbls = max(int(q["minimum_vbls"]), 1500)

    OUT.mkdir(parents=True, exist_ok=True)
    HD.mkdir(parents=True, exist_ok=True)
    RESULT.unlink(missing_ok=True)

    compile_cmd = [
        "m68k-atari-mint-gcc",
        "-m68000",
        "-O2",
        "-s",
        "-o",
        str(PROBE),
        str(SOURCE),
    ]
    cp = subprocess.run(compile_cmd, cwd=ROOT)
    if cp.returncode != 0:
        fail(f"guest probe compile exit {cp.returncode}")

    (OUT / "PROBE.sha256").write_text(f"{sha256(PROBE)}  AESVDI.PRG\n", encoding="utf-8")
    (OUT / "ROM.sha256").write_text(f"{sha256(ROM)}  {ROM.name}\n", encoding="utf-8")
    (OUT / "PROFILE.json").write_text(
        json.dumps(profile, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )

    effective = {
        "profile_id": profile["id"],
        "machine": machine["hatari_machine"],
        "cpu_level": machine["cpu_level"],
        "st_ram_mib": ram_mib,
        "run_vbls": run_vbls,
        "guest_program": r"C:\AESVDI.PRG",
        "result_file": r"C:\M2AESVD.TXT",
    }
    (OUT / "HATARI_PROFILE.json").write_text(
        json.dumps(effective, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )

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
        "--harddrive", str(HD),
        "--protect-hd", "off",
        "--gemdos-case", "upper",
        "--auto", r"C:\AESVDI.PRG",
        "--log-file", str(LOG),
    ]

    runner = ["xvfb-run", "-a"] if shutil.which("xvfb-run") else []
    cp = subprocess.run(runner + cmd, cwd=ROOT)
    if cp.returncode != 0:
        fail(f"Hatari exit {cp.returncode}")

    log_text = LOG.read_text(encoding="utf-8", errors="replace") if LOG.exists() else ""
    lowered = log_text.lower()
    for marker in FATAL_MARKERS:
        if marker in lowered:
            fail(f"fatal marker in Hatari log: {marker}")

    if not RESULT.is_file():
        fail("guest result missing")

    result_text = RESULT.read_text(encoding="ascii", errors="replace").replace("\r\n", "\n")
    fields = {}
    for line in result_text.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            fields[key.strip()] = value.strip()

    if fields.get("schema") != "1":
        fail("guest result schema")
    if fields.get("profile") != profile["id"]:
        fail("guest result profile")
    if fields.get("status") != "PASS":
        fail(f"guest verdict {fields.get('status', 'missing')} stage={fields.get('stage', 'unknown')}")
    if int(fields.get("aes_app_id", "-1")) < 0:
        fail("invalid AES application id")
    if int(fields.get("phys_handle", "0")) <= 0:
        fail("invalid physical workstation handle")
    if int(fields.get("vdi_handle", "0")) <= 0:
        fail("invalid virtual workstation handle")

    normalized = "\n".join(f"{k}={fields[k]}" for k in sorted(fields)) + "\n"
    (OUT / "RESULT.txt").write_text(normalized, encoding="utf-8")
    print(f"M2.4 AES/VDI regression: PASS ({profile['id']})")


if __name__ == "__main__":
    main()
