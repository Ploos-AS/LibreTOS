# M1 Qualification — Reproducible ST/68000 Baseline

## Objective

M1 proves that LibreTOS can obtain a fully redistributable, pinned TOS-compatible baseline, build a 68000 Atari ST ROM reproducibly, and boot-smoke-test that ROM in Hatari without any proprietary Atari ROM image.

## Pinned inputs

- EmuTOS repository: `https://github.com/emutos/emutos.git`
- EmuTOS commit: `e0f0c2333d39a487e73d8b17f62b70a95441cd32`
- Build mode: EmuTOS `ELF=1`, `UNIQUE=us`, target `192`
- Toolchain archive SHA-256: `b01d56c0f70dc594ca20e713190ee73d39075ce79ff2de972bb57b95b65e688a`

The exact machine-readable pins live in `config/upstream.env`.

## Target profile

- Atari ST
- Motorola 68000
- 1 MiB ST-RAM for emulator qualification
- 192 KiB ROM image
- US single-country build
- Hatari machine profile: `st`
- Hatari CPU level: `0` (68000)

## Qualification

Run:

```sh
make qualify-m1
```

This performs:

1. Verified download of the pinned 68000-safe `m68k-elf` toolchain.
2. Fresh clone and detached checkout of the exact EmuTOS commit.
3. `m68k-elf`/68000 build of a 192 KiB ROM.
4. SHA-256 generation and build metadata capture.
5. Hatari boot smoke test for 500 VBLs with original Atari TOS ROMs absent.
6. Failure on non-zero Hatari exit or fatal ROM/emulation markers.

## Artifacts

The local build writes:

- `build/m1/libretos-m1-st-us.img`
- `build/m1/SHA256SUMS`
- `build/m1/BUILDINFO.txt`
- `build/m1/hatari.log`

## Interpretation

Passing M1 establishes a reproducible and freely redistributable baseline suitable for LibreTOS development. It does **not** claim that the baseline is an independent LibreTOS implementation; at M1 it remains explicitly derived from the pinned EmuTOS upstream.
