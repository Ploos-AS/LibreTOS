# M5.4 TT030 enhanced hardware/interface qualification

M5.4 extends the canonical TT030 target beyond boot and machine identity with a guest-side probe for deterministic TT-specific interfaces exposed by the pinned free ROM under Hatari.

Canonical profile: `tt030-68030-4m-16mtt-512k-us`.

The M5.4 probe qualifies:

- `_VDO == 0x00020000` (TT video family),
- `_FPU` cookie presence while Hatari is configured with a 68882,
- `_SND` PSG + 8-bit DMA sound discovery,
- `_FRB` presence when TT-RAM is enabled.

The runtime remains the M5 canonical TT configuration: Hatari `tt`, 68030 at 32 MHz, 4 MiB ST-RAM, 16 MiB TT-RAM, 32-bit addressing, 68882 and MMU enabled.

This milestone intentionally does **not** claim complete VME, SCSI, SCC or NVRAM-persistence qualification. Those interfaces are either incompletely modelled, require external devices, or are not appropriate for a deterministic CI claim. Machine-profile feature presence and runtime-qualified behavior remain separate concepts.

Run locally with:

```sh
make qualify-m5-enhanced
```

Evidence is written under `build/m5/tt030-enhanced/` and uploaded by the dedicated GitHub Actions workflow.
