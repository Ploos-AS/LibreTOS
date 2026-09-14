# M5.5 — Atari TT030 aggregate qualification

M5.5 is the final qualification gate for the canonical LibreTOS Atari TT030 target.

Run:

```sh
make qualify-m5
```

The aggregate gate executes, in order:

1. **M5.1** — canonical TT030 profile validation
2. **M5.2** — dedicated 512 KiB ROM build and Hatari boot qualification
3. **M5.3** — guest-side TT030 platform/API qualification
4. **M5.4** — deterministic TT030 enhanced hardware/interface qualification

The gate stops on the first failure and records `build/m5/qualification/RESULT.json`.
A complete pass records the canonical profile and a PASS result for every M5.1–M5.4 stage.

## Qualified scope

A M5.5 PASS supports the canonical profile:

- Atari TT030
- 68030 at 32 MHz
- 4 MiB ST-RAM
- 16 MiB TT-RAM
- 32-bit addressing
- 68882 FPU configuration
- 512 KiB LibreTOS US ROM artifact
- Hatari-based automated qualification

The runtime claim includes the behavior already covered by M5.2–M5.4, including machine/CPU identity, TT-RAM, screen-base sanity, TT video discovery, FPU discovery, DMA-sound discovery and FRB presence.

## Explicit exclusions

M5.5 does **not** claim complete qualification of:

- VME bus behavior
- complete SCSI semantics
- SCC traffic
- NVRAM persistence

Those interfaces remain outside the required automated TT030 compatibility claim until deterministic emulator/runtime coverage exists.

## Target status

`config/targets.json` may only mark `tt030-68030` as `qualified` after the M5.5 aggregate workflow has passed on GitHub Actions.
