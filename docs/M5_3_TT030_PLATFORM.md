# M5.3 — Atari TT030 guest-side platform qualification

M5.3 verifies that the canonical LibreTOS TT030 image does more than boot: a native 68k guest probe must observe the expected TT platform contract while running under Hatari.

## Command

```sh
make qualify-m5-platform
```

## Canonical runtime

- profile: `tt030-68030-4m-16mtt-512k-us`
- Hatari machine: `tt`
- CPU: 68030, level 3, 32 MHz
- addressing: 32-bit
- ST-RAM: 4 MiB
- TT-RAM: 16 MiB
- FPU: 68882
- MMU: enabled
- ROM: `LibreTOS-TT030-68030-512k-us.img`

## Guest assertions

The guest program `tests/m5/tt030_platform_probe.c` records and validates:

- `_MCH` identifies the TT family
- `_CPU` identifies a 68030
- the TOS `_ramtop` system variable reports TT-RAM above the 16 MiB boundary
- canonical initial resolution remains ST-low for this profile
- physical and logical screen bases are present and aligned

The host-side qualifier independently parses and re-validates those guest observations. A missing result file, bad schema/profile, guest failure stage, Hatari fatal marker, timeout, or mismatched platform value fails M5.3.

## Evidence

Evidence is written below `build/m5/tt030-platform/`:

- `PROFILE.json`
- `ROM.sha256`
- `PROBE.sha256`
- `HATARI_PROFILE.json`
- `hatari.log`
- `GUEST_RESULT.txt`
- `RESULT.json`
- `RESULT.txt`

This milestone is scoped to deterministic platform identity and memory/video basics. Deeper TT-specific hardware/interface qualification remains a later M5 step.
