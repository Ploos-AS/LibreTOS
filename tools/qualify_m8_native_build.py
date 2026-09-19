#!/usr/bin/env python3
from pathlib import Path
import struct
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
out = root / "build" / "m8" / "native"

elf = out / "LibreTOS-Amiga-OCS-68000-1M.elf"
binary = out / "LibreTOS-Amiga-OCS-68000-1M.bin"

for path in (elf, binary):
    if not path.is_file() or path.stat().st_size == 0:
        raise SystemExit(f"missing native artifact: {path}")

data = binary.read_bytes()
if len(data) < 8:
    raise SystemExit("native image is shorter than the Amiga reset vector")
ssp, pc = struct.unpack(">II", data[:8])
if ssp == 0 or pc == 0:
    raise SystemExit("native image has invalid reset vectors")
if pc & 1:
    raise SystemExit("native reset PC is not even")
print("M8 native Amiga 68000 artifact: PASS")
