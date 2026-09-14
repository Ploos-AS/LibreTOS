# M1 Qualification — Reproducible baseline + Hatari boot

Status: **PASS (CI)**

LibreTOS M1 establishes a reproducible free Atari ST / Motorola 68000 ROM baseline and verifies that the produced image boots under Hatari without requiring proprietary Atari ROM material.

## Qualified baseline

- Target: Atari ST
- CPU: Motorola 68000
- ROM size/profile: 192 KiB, US
- Reference baseline: pinned EmuTOS commit from `config/upstream.env`
- Toolchain: `m68k-atari-mint-gcc`
- Emulator: Hatari

## Qualification path

The canonical command is:

```sh
make qualify-m1
```

This clones and checks out the exact pinned upstream commit, builds the 192 KiB US ROM, records SHA-256/build metadata, and boots it in Hatari using the ST/68000 profile. Qualification fails on Hatari startup failure or known fatal log markers.

## CI evidence

GitHub Actions CI run **34598722883** for commit `6671e1e985cf2f624f3b38ab80fe9e3f516e0aaa` completed successfully on 2026-09-11.

The workflow archives:

- `build/m1/SHA256SUMS`
- `build/m1/BUILDINFO.txt`
- `build/m1/hatari.log`

## M1 exit criteria

- [x] audited/pinned upstream baseline
- [x] cross-toolchain defined
- [x] clean scripted build
- [x] build hash and metadata recorded
- [x] Atari ST / 68000 Hatari profile
- [x] automated boot smoke test
- [x] qualification evidence archived by CI

## Scope

M1 proves that the pinned free baseline can be built by the project workflow and reaches a successful Hatari boot smoke test. It does **not** yet claim broad TOS API compatibility or independence from the EmuTOS baseline. Those claims belong to M2 and later milestones.
