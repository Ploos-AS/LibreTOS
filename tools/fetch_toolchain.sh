#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
# shellcheck disable=SC1091
source "$ROOT/config/upstream.env"

CACHE_DIR=${CACHE_DIR:-"$ROOT/.cache"}
TOOLCHAIN_DIR=${TOOLCHAIN_DIR:-"$CACHE_DIR/m68k-elf"}
ARCHIVE="$CACHE_DIR/m68k-elf-toolchain.tar.gz"

mkdir -p "$CACHE_DIR"

if [[ -x "$TOOLCHAIN_DIR/bin/m68k-elf-gcc" ]]; then
    echo "toolchain already present: $TOOLCHAIN_DIR"
    exit 0
fi

curl -L --fail --retry 3 -o "$ARCHIVE" "$TOOLCHAIN_URL"
echo "$TOOLCHAIN_SHA256  $ARCHIVE" | sha256sum -c -

rm -rf "$TOOLCHAIN_DIR"
mkdir -p "$TOOLCHAIN_DIR"
tar -xzf "$ARCHIVE" -C "$TOOLCHAIN_DIR" --strip-components=1

"$TOOLCHAIN_DIR/bin/m68k-elf-gcc" --version | head -1
