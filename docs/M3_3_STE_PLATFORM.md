# M3.3 — Atari STe platform/XBIOS qualification

M3.3 moves beyond boot-only qualification and verifies that the dedicated LibreTOS STe target exposes the expected Atari STe platform identity and core XBIOS-visible hardware capabilities inside the guest.

## Canonical target

- Profile: `ste-68000-1m-256k-us`
- Machine: Atari STe
- CPU: Motorola 68000
- ST-RAM: 1 MiB
- ROM: `LibreTOS-STe-68000-256k-us.img`
- Emulator: Hatari, `--machine ste`

## Guest probe

`tests/m3/ste_platform_probe.c` runs as a native TOS program and records its verdict in `C:\M3STE.TXT`.

The probe checks:

1. `_MCH` cookie identifies the STe machine family (`0x0001xxxx`).
2. `_SND` advertises both PSG sound and stereo DMA sound (bits 0 and 1).
3. `Getrez()` reports the canonical ST-low boot resolution.
4. `Physbase()` and `Logbase()` return valid aligned screen addresses.
5. `Blitmode(-1)` reports that a blitter is present.

Cookie-jar access is performed in supervisor mode through `Supexec()`. The checks deliberately use documented TOS/XBIOS interfaces instead of hard-coded internal EmuTOS locations.

## Host qualification

`tools/qualify_m3_ste_platform.py`:

- builds the guest probe with `m68k-atari-mint-gcc -m68000`;
- builds/uses the dedicated 256 KiB STe ROM;
- boots the canonical STe profile in Hatari;
- attaches a writable GEMDOS drive as `C:`;
- auto-starts `C:\STEPLAT.TOS`;
- validates the guest result and selected values again host-side;
- rejects real Hatari `ERROR:`/`FATAL:` or ROM-load failures;
- bounds Hatari runtime with the same timeout discipline used by M3.2.

Evidence is written beneath `build/m3/ste-platform/` and uploaded by CI even when qualification fails.

## Evidence

- `PROFILE.json`
- `ROM.sha256`
- `PROBE.sha256`
- `HATARI_PROFILE.json`
- `RESULT.txt`
- `hatari.log`

## Status

Implemented. CI qualification determines PASS/FAIL.
