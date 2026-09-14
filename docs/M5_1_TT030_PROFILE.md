# M5.1 — Canonical Atari TT030 profile

M5 starts the TT030 family while retaining every earlier Atari target.

Canonical profile: `tt030-68030-4m-16mtt-512k-us`

## Machine contract

- Atari TT030
- Hatari machine: `tt`
- Motorola 68030 (`cpu_level=3`)
- 32 MHz CPU clock
- 32-bit addressing
- 4 MiB ST-RAM
- 16 MiB TT-RAM
- 512 KiB US LibreTOS ROM artifact
- artifact name: `LibreTOS-TT030-68030-512k-us.img`

The 512 KiB ROM size follows the pinned free baseline build contract. Hatari documents the TT as a 32 MHz 68030 machine and supports separate TT-RAM plus 32-bit addressing in TT mode.

## Platform contract

The profile records TT-class interfaces that later M5 runtime stages can qualify where Hatari provides deterministic support: TT video, TT-RAM, MMU, FPU, second MFP, SCC, NVRAM/RTC, SCSI and VME presence.

A profile feature does not by itself claim complete functional emulation. In particular, future runtime qualification must distinguish between machine-contract presence and interfaces Hatari can actually exercise reliably.

## Regression rule

TT030 work must not replace or weaken the previously qualified ST, STe, Mega ST or Mega STe targets. M5.1 therefore declares all four profiles as mandatory regressions.

## Qualification

Run:

```sh
make qualify-m5-profile
```

M5.1 is static/profile qualification only. Dedicated 512 KiB TT030 ROM construction and Hatari boot qualification belong to M5.2.
