#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
# shellcheck disable=SC1091
source "$ROOT/config/upstream.env"

SRC_DIR=${SRC_DIR:-"$ROOT/build/emutos-m3-ste"}
OUT_DIR=${OUT_DIR:-"$ROOT/build/m3/ste"}
ARTIFACT="$OUT_DIR/LibreTOS-STe-68000-256k-us.img"

command -v m68k-atari-mint-gcc >/dev/null 2>&1 || {
    echo "m68k-atari-mint-gcc not found" >&2
    exit 1
}

rm -rf "$SRC_DIR" "$OUT_DIR"
mkdir -p "$(dirname "$SRC_DIR")" "$OUT_DIR"

git clone --filter=blob:none "$EMUTOS_REPO" "$SRC_DIR"
git -C "$SRC_DIR" checkout --detach "$EMUTOS_COMMIT"
ACTUAL=$(git -C "$SRC_DIR" rev-parse HEAD)
[[ "$ACTUAL" == "$EMUTOS_COMMIT" ]]

make -C "$SRC_DIR" UNIQUE=us 256

ROM="$SRC_DIR/etos256us.img"
test -f "$ROM"
cp "$ROM" "$ARTIFACT"
sha256sum "$ARTIFACT" | tee "$OUT_DIR/SHA256SUMS"
{
    echo "emutos_commit=$EMUTOS_COMMIT"
    echo "compiler=$(m68k-atari-mint-gcc --version | head -1)"
    echo "toolchain=m68k-atari-mint"
    echo "profile=ste-68000-1m-256k-us"
    echo "target=Atari STe / 68000 / 256 KiB / US"
    echo "artifact=$(basename "$ARTIFACT")"
} > "$OUT_DIR/BUILDINFO.txt"

stat -c 'ROM size: %s bytes' "$ARTIFACT"
