# M6.3 — Falcon030 platform qualification

M6.3 moves beyond the M6.2 boot gate and verifies the canonical Falcon030 target from inside the guest.

The native Atari/MiNT probe runs under the dedicated 512 KiB LibreTOS Falcon030 ROM in Hatari and records deterministic platform identity evidence.

## Required guest observations

- `_MCH` identifies the Falcon family (family value 3).
- `_CPU` reports 68030 (`30`).
- `_VDO` identifies Falcon video (family value 3).
- `Physbase()` and `Logbase()` return non-zero, aligned screen addresses.

The probe also records `Getrez()` for evidence, but M6.3 deliberately does not impose an ST-compatible resolution value on Falcon. Falcon enhanced interfaces such as VIDEL modes, DSP, DMA audio and IDE are reserved for M6.4 and are not claimed by this gate.

## Qualification

Run:

```sh
make qualify-m6-platform
```

Evidence is written below `build/m6/falcon030-platform/`, including the effective Hatari profile, ROM/probe SHA-256 values, Hatari log, normalized guest result and final machine-readable verdict.

GitHub Actions workflow `M6 Platform` runs the same gate on `ubuntu-latest` and uploads both evidence and the exact ROM artifact used for qualification.
