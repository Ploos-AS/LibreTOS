#!/usr/bin/env python3
"""Build a deterministic 720 KiB Atari ST FAT12 floppy with AUTO programs.

The image is intentionally generated with the Python standard library so CI does
not depend on mtools or host filesystem mounting.  It is a normal 80-track,
2-sided, 9-sector FAT12 disk suitable for Hatari's --disk-a option.
"""
from __future__ import annotations

import argparse
import struct
from pathlib import Path

SECTOR = 512
SECTORS = 1440
SECTORS_PER_CLUSTER = 2
FAT_SECTORS = 3
ROOT_ENTRIES = 112
ROOT_SECTORS = 7
RESERVED = 1
FATS = 2
DATA_START = RESERVED + FATS * FAT_SECTORS + ROOT_SECTORS
IMAGE_SIZE = SECTOR * SECTORS
CLUSTER_SIZE = SECTORS_PER_CLUSTER * SECTOR


def _name83(name: str) -> bytes:
    base, dot, ext = name.upper().partition('.')
    if not base or len(base) > 8 or len(ext) > 3:
        raise ValueError(f'not an 8.3 filename: {name}')
    return base.encode('ascii').ljust(8) + ext.encode('ascii').ljust(3)


def _fat12_set(fat: bytearray, cluster: int, value: int) -> None:
    off = cluster + cluster // 2
    if cluster & 1:
        fat[off] = (fat[off] & 0x0F) | ((value << 4) & 0xF0)
        fat[off + 1] = (value >> 4) & 0xFF
    else:
        fat[off] = value & 0xFF
        fat[off + 1] = (fat[off + 1] & 0xF0) | ((value >> 8) & 0x0F)


def _dirent(name: str, attr: int, cluster: int, size: int) -> bytes:
    ent = bytearray(32)
    if name == '.':
        ent[:11] = b'.          '
    elif name == '..':
        ent[:11] = b'..         '
    else:
        ent[:11] = _name83(name)
    ent[11] = attr
    struct.pack_into('<H', ent, 26, cluster)
    struct.pack_into('<I', ent, 28, size)
    return bytes(ent)


def build_auto_floppy(path: Path, program_name: str, program: bytes) -> None:
    """Create an Atari GEMDOS-compatible 720 KiB FAT12 image with AUTO/<program>."""
    image = bytearray(IMAGE_SIZE)

    # Atari GEMDOS floppy BPB. Classic TOS expects two 512-byte sectors per
    # cluster on 720 KiB media; using one sector can leave the volume unreadable
    # to GEMDOS even though host FAT parsers accept it.
    boot = memoryview(image)[:SECTOR]
    boot[0:2] = b'\x60\x1c'
    boot[2:8] = b'LIBRE '
    boot[8:11] = b'TOS'
    struct.pack_into('<H', boot, 11, SECTOR)
    boot[13] = SECTORS_PER_CLUSTER
    struct.pack_into('<H', boot, 14, RESERVED)
    boot[16] = FATS
    struct.pack_into('<H', boot, 17, ROOT_ENTRIES)
    struct.pack_into('<H', boot, 19, SECTORS)
    boot[21] = 0xF9
    struct.pack_into('<H', boot, 22, FAT_SECTORS)
    struct.pack_into('<H', boot, 24, 9)
    struct.pack_into('<H', boot, 26, 2)
    struct.pack_into('<H', boot, 28, 0)

    fat = bytearray(FAT_SECTORS * SECTOR)
    fat[0:3] = b'\xF9\xFF\xFF'

    auto_cluster = 2
    _fat12_set(fat, auto_cluster, 0xFFF)
    needed = max(1, (len(program) + CLUSTER_SIZE - 1) // CLUSTER_SIZE)
    first_program_cluster = 3
    last_program_cluster = first_program_cluster + needed - 1
    data_clusters = (SECTORS - DATA_START) // SECTORS_PER_CLUSTER
    max_cluster = data_clusters + 1
    if last_program_cluster > max_cluster:
        raise ValueError('program does not fit on floppy')
    for cluster in range(first_program_cluster, last_program_cluster + 1):
        _fat12_set(fat, cluster, 0xFFF if cluster == last_program_cluster else cluster + 1)

    for copy in range(FATS):
        start = (RESERVED + copy * FAT_SECTORS) * SECTOR
        image[start:start + len(fat)] = fat

    root_start = (RESERVED + FATS * FAT_SECTORS) * SECTOR
    image[root_start:root_start + 32] = _dirent('AUTO', 0x10, auto_cluster, 0)

    auto_off = (DATA_START + (auto_cluster - 2) * SECTORS_PER_CLUSTER) * SECTOR
    image[auto_off:auto_off + 32] = _dirent('.', 0x10, auto_cluster, 0)
    image[auto_off + 32:auto_off + 64] = _dirent('..', 0x10, 0, 0)
    image[auto_off + 64:auto_off + 96] = _dirent(program_name, 0x20, first_program_cluster, len(program))

    pos = 0
    for cluster in range(first_program_cluster, last_program_cluster + 1):
        off = (DATA_START + (cluster - 2) * SECTORS_PER_CLUSTER) * SECTOR
        chunk = program[pos:pos + CLUSTER_SIZE]
        image[off:off + len(chunk)] = chunk
        pos += len(chunk)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(image)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('image', type=Path)
    ap.add_argument('program', type=Path)
    ap.add_argument('--name', required=True)
    args = ap.parse_args()
    build_auto_floppy(args.image, args.name, args.program.read_bytes())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
