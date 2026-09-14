# M6.1 — Atari Falcon030 canonical profile

M6.1 introduces the permanent Atari Falcon030/68030 machine profile while retaining every previously qualified LibreTOS target.

Canonical profile: `config/m6-falcon030-68030.json`

## Machine contract

- Atari Falcon030
- Motorola 68030, Hatari CPU level 3
- 16 MHz canonical CPU clock
- 4 MiB ST-RAM
- 32-bit addressing
- 512 KiB free/pinned LibreTOS ROM baseline
- Hatari machine type `falcon`

The Falcon platform feature inventory records the machine contract, not a claim that every interface has already passed runtime qualification. Later M6 milestones must independently prove boot, guest-visible platform identity and deterministic Falcon-specific interfaces before the target can become `qualified`.

Tracked platform characteristics include Falcon video, blitter, DMA sound, DSP56001, IDE, NVRAM/RTC and the 68030 MMU. Falcon FPU support is recorded as optional because it was not standard on every stock Falcon030 configuration.

## Regression policy

M6 must retain and regress all previously qualified variants:

- Atari ST
- Atari STe
- Atari Mega ST
- Atari Mega STe
- Atari TT030

No prior ROM artifact or profile may be replaced by the Falcon target.

## Qualification

Run:

```sh
make qualify-m6-profile
```

M6.1 passes only when the canonical profile, target registry contract, free-ROM policy and full prior-target regression list are consistent.
