# M6.4 — Falcon030 enhanced interfaces

M6.4 adds deterministic guest-side qualification for enhanced Falcon030 facilities that can be asserted reliably on the GitHub Hatari runner.

## Qualified

- Falcon VIDEL identification through the `_VDO` cookie (Falcon family value).
- Falcon sound capability discovery through the `_SND` cookie with at least one advertised sound capability.
- The `_FPU` cookie is captured as evidence but is not required because the canonical M6 profile defines the FPU as optional.

Hatari is run as a Falcon030 with 68030, 16 MHz, 4 MiB ST-RAM, 32-bit addressing, MMU enabled and 44.1 kHz sound. The guest probe is compiled with the pinned Atari/MiNT toolchain and writes a machine-readable result into the GEMDOS drive.

## Explicitly not claimed yet

M6.4 does **not** claim full DSP56001 execution semantics, IDE read/write semantics, NVRAM persistence, or external audio fidelity. Those interfaces need dedicated deterministic fixtures before they can become compatibility claims.

## Evidence

`make qualify-m6-enhanced` writes evidence below `build/m6/falcon030-enhanced/`, including the effective Hatari profile, ROM/probe hashes, Hatari log, normalized guest result and final JSON/text verdict.
