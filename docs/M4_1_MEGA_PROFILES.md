# M4.1 — Canonical Mega ST / Mega STe profiles

M4 starts the workstation branch of the permanent Atari target matrix. Mega ST and Mega STe are separate retained targets; neither replaces the ST or STe artifacts.

## Canonical Mega ST profile

- profile: `mega-st-68000-4m-192k-us`
- Hatari machine: `megast`
- CPU: Motorola 68000, 8 MHz
- ST-RAM: 4 MiB
- ROM: 192 KiB, US, pinned free baseline
- display baseline: ST-low, 16 colors from the 512-color ST palette
- required hardware contract: blitter and Mega real-time clock
- explicitly absent from the canonical contract: STe enhanced shifter, DMA sample sound, hardware scrolling
- regression dependency: canonical M2 ST profile

## Canonical Mega STe profile

- profile: `mega-ste-68000-4m-256k-us`
- Hatari machine: `megaste`
- CPU: Motorola 68000, canonical 16 MHz mode
- ST-RAM: 4 MiB
- ROM: 256 KiB, US, pinned free baseline
- display baseline: ST-low, 16 colors from the 4096-color STe palette
- required hardware contract: STe enhanced shifter, DMA sound, blitter, hardware scrolling, RTC, 16 MHz mode, VME and SCC presence
- regression dependencies: canonical M3 STe profile and canonical Mega ST profile

## Qualification

`make qualify-m4-profiles` validates both profile files against the permanent target registry. CI runs this as the `m4-profiles` job.

This milestone defines configuration contracts only. Dedicated ROM build, boot and hardware qualification follow in later M4 sub-milestones.
