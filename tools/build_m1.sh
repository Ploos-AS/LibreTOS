#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
# shellcheck disable=SC1091
source "$ROOT/config/upstream.env"

CACHE_DIR=${CACHE_DIR:-"$ROOT/.cache"}
TOOLCHAIN_DIR=${TOOLCHAIN_DIR:-"$CACHE_DIR/m68k-elf"}
SRC_DIR=${SRC_DIR:-"$ROOT/build/emutos"}
OUT_DIR=${OUT_DIR:-"$ROOT/build/m1"}

if [[ ! -x "$TOOLCHAIN_DIR/bin/m68k-elf-gcc" ]]; then
    "$ROOT/tools/fetch_toolchain.sh"
fi

rm -rf "$SRC_DIR" "$OUT_DIR"
mkdir -p "$(dirname "$SRC_DIR")" "$OUT_DIR"

git clone --filter=blob:none "$EMUTOS_REPO" "$SRC_DIR"
git -C "$SRC_DIR" checkout --detach "$EMUTOS_COMMIT"
ACTUAL=$(git -C "$SRC_DIR" rev-parse HEAD)
[[ "$ACTUAL" == "$EMUTOS_COMMIT" ]]

export PATH="$TOOLCHAIN_DIR/bin:$PATH"
make -C "$SRC_DIR" ELF=1 UNIQUE=us 192

ROM="$SRC_DIR/etos192us.img"
test -f "$ROM"
cp "$ROM" "$OUT_DIR/libretos-m1-st-us.img"
sha256sum "$OUT_DIR/libretos-m1-st-us.img" | tee "$OUT_DIR/SHA256SUMS"
{
    echo "emutos_commit=$EMUTOS_COMMIT"
    echo "toolchain_sha256=$TOOLCHAIN_SHA256"
    echo "compiler=$(m68k-elf-gcc --version | head -1)"
    echo "target=Atari ST / 68000 / 192 KiB / US"
} > "$OUT_DIR/BUILDINFO.txt"

stat -c 'ROM size: %s bytes' "$OUT_DIR/libretos-m1-st-us.img"
