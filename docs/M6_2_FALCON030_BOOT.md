# M6.2 — Atari Falcon030 ROM build and boot qualification

M6.2 establishes the permanent LibreTOS Falcon030 ROM artifact and a profile-driven Hatari boot regression.

## Canonical artifact

- Profile: `config/m6-falcon030-68030.json`
- Artifact: `LibreTOS-Falcon030-68030-512k-us.img`
- ROM size: 512 KiB
- Source: pinned free EmuTOS baseline from `config/upstream.env`
- Toolchain: `m68k-atari-mint`

The build writes `SHA256SUMS` and `BUILDINFO.txt` next to the ROM.

## Canonical Hatari boot contract

- machine: Falcon
- CPU: 68030, level 3
- CPU clock: 16 MHz
- ST-RAM: 4 MiB
- fast RAM: none
- 32-bit addressing
- MMU: enabled
- FPU: optional, not required for M6.2
- sound: disabled for deterministic boot smoke
- minimum runtime: profile `minimum_vbls`

M6.2 is a boot qualification only. It does not claim Falcon-specific DSP, VIDEL, audio, IDE, NVRAM or other enhanced-interface qualification. Those are covered by later M6 milestones.

## Evidence

`make qualify-m6-boot` produces:

- `build/m6/falcon030/LibreTOS-Falcon030-68030-512k-us.img`
- `build/m6/falcon030/SHA256SUMS`
- `build/m6/falcon030/BUILDINFO.txt`
- `build/m6/falcon030-boot/PROFILE.json`
- `build/m6/falcon030-boot/ROM.sha256`
- `build/m6/falcon030-boot/HATARI_PROFILE.txt`
- `build/m6/falcon030-boot/hatari.log`
- `build/m6/falcon030-boot/RESULT.json`
- `build/m6/falcon030-boot/RESULT.txt`

GitHub Actions workflow `M6 Boot` runs the same gate and uploads the evidence and ROM artifact.
