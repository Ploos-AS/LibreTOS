#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
# shellcheck disable=SC1091
source "$ROOT/config/upstream.env"

SRC_DIR=${SRC_DIR:-"$ROOT/build/emutos-m4-mega"}
OUT_DIR=${OUT_DIR:-"$ROOT/build/m4/mega"}
MEGAST_ARTIFACT="$OUT_DIR/LibreTOS-MegaST-68000-192k-us.img"
MEGASTE_ARTIFACT="$OUT_DIR/LibreTOS-MegaSTe-68000-256k-us.img"

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

make -C "$SRC_DIR" UNIQUE=us 192
MEGAST_ROM="$SRC_DIR/etos192us.img"
test -f "$MEGAST_ROM"
cp "$MEGAST_ROM" "$MEGAST_ARTIFACT"

make -C "$SRC_DIR" clean
make -C "$SRC_DIR" UNIQUE=us 256
MEGASTE_ROM="$SRC_DIR/etos256us.img"
test -f "$MEGASTE_ROM"
cp "$MEGASTE_ROM" "$MEGASTE_ARTIFACT"

(
    cd "$OUT_DIR"
    sha256sum "$(basename "$MEGAST_ARTIFACT")" "$(basename "$MEGASTE_ARTIFACT")" > SHA256SUMS
)

{
    echo "emutos_commit=$EMUTOS_COMMIT"
    echo "compiler=$(m68k-atari-mint-gcc --version | head -1)"
    echo "toolchain=m68k-atari-mint"
    echo "mega_st_profile=mega-st-68000-4m-192k-us"
    echo "mega_st_artifact=$(basename "$MEGAST_ARTIFACT")"
    echo "mega_ste_profile=mega-ste-68000-4m-256k-us"
    echo "mega_ste_artifact=$(basename "$MEGASTE_ARTIFACT")"
} > "$OUT_DIR/BUILDINFO.txt"

stat -c 'Mega ST ROM size: %s bytes' "$MEGAST_ARTIFACT"
stat -c 'Mega STe ROM size: %s bytes' "$MEGASTE_ARTIFACT"
