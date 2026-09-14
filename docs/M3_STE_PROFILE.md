# M3.1 — Canonical Atari STe / 68000 profile

Status: **implemented; CI qualification pending**.

M3.1 adds the first permanent LibreTOS target after the qualified Atari ST baseline. It extends the machine matrix; it does not replace the ST build.

## Canonical profile

The machine-readable profile is `config/m3-ste-68000.json` with id `ste-68000-1m-192k-us`.

Baseline assumptions:

- Atari STe family
- representative models: 520STe and 1040STe
- Motorola 68000 at 8 MHz
- 1 MiB ST-RAM
- 192 KiB US free ROM baseline
- color monitor, ST-low initial resolution
- STe enhanced shifter / 4096-color palette space
- DMA sound present
- blitter present
- hardware scrolling present
- one floppy drive, ROM boot
- Hatari `ste` machine profile for automated qualification

The canonical artifact name is `LibreTOS-STe-68000-192k-us.img`.

## Regression rule

The existing `st-68000-1m-192k-us` target remains independently qualified. Every later STe qualification gate must retain ST regression coverage rather than turning the ST profile into an STe profile.

## Qualification

Run the static profile contract with:

```sh
make qualify-m3-profile
```

M3.1 establishes the machine contract only. Subsequent M3 stages will add STe boot/runtime and STe-specific BIOS/XBIOS, video, DMA sound and blitter regressions before the target becomes `qualified`.
