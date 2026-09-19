#!/bin/sh
set -eu

OUT=${1:-build/m8/native}
mkdir -p "$OUT"

CC=${AMIGA_CC:-m68k-amigaos-gcc}
OBJCOPY=${AMIGA_OBJCOPY:-m68k-amigaos-objcopy}
CFLAGS="-m68000 -ffreestanding -fno-builtin -fno-stack-protector"
LDFLAGS="-nostdlib -Wl,-T,linker/m8-amiga-native.ld"

"$CC" $CFLAGS -c src/amiga/m8_native_boot.s -o "$OUT/m8_native_boot.o"
"$CC" $LDFLAGS "$OUT/m8_native_boot.o" -o "$OUT/LibreTOS-Amiga-OCS-68000-1M.elf"
"$OBJCOPY" -O binary "$OUT/LibreTOS-Amiga-OCS-68000-1M.elf" "$OUT/LibreTOS-Amiga-OCS-68000-1M.bin"

test -s "$OUT/LibreTOS-Amiga-OCS-68000-1M.elf"
test -s "$OUT/LibreTOS-Amiga-OCS-68000-1M.bin"

python3 - "$OUT/LibreTOS-Amiga-OCS-68000-1M.bin" "$OUT/LibreTOS-Amiga-OCS-68000-1M.rom" <<'PY'
import pathlib, sys
src, dst = map(pathlib.Path, sys.argv[1:])
data = src.read_bytes()
if len(data) > 524288:
    raise SystemExit("native image exceeds 512 KiB ROM envelope")
rom = data + bytes(524288 - len(data))
dst.write_bytes(rom)
print(f"wrote {dst} ({len(rom)} bytes)")
PY

test "$(wc -c < "$OUT/LibreTOS-Amiga-OCS-68000-1M.rom")" -eq 524288

printf '%s\n' "M8 native Amiga 68000 build: PASS"
