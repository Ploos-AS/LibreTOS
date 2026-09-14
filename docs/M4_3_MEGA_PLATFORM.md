# M4.3 — Mega ST / Mega STe platform qualification

M4.3 adds guest-side platform probes for the retained Mega ST and Mega STe LibreTOS variants.

## Canonical targets

- Mega ST: `mega-st-68000-4m-192k-us`
- Mega STe: `mega-ste-68000-4m-256k-us`

The probe is compiled separately for each target and run from a writable GEMDOS hard-drive folder under Hatari.

## Qualified guest-visible contracts

Both targets must:

- boot the dedicated M4.2 ROM artifact;
- run a native 68000 guest probe;
- report ST-low through `Getrez()`;
- expose valid even physical/logical screen bases;
- report a blitter through `Blitmode(-1)`.

Mega ST additionally must not identify as an STe-family machine and must not advertise the DMA-sound capability bit.

Mega STe must identify as the STe family through `_MCH` and must advertise PSG plus DMA sound through `_SND`.

These checks deliberately avoid requiring functional VME transactions. Hatari can model the Mega STe machine profile without providing a qualification-grade emulation contract for every expansion-bus feature.

## Run

```sh
make qualify-m4-platform
```

The target rebuilds the retained M4.2 ROMs and runs both guest probes.

## Evidence

Evidence is written under:

- `build/m4/mega-platform/megast/`
- `build/m4/mega-platform/megaste/`
- `build/m4/mega-platform/RESULT.json`

Each target records its profile, ROM checksum, probe checksum, effective Hatari settings, Hatari log, and normalized guest result.

A PASS claim is scoped to these canonical Hatari profiles and the observable contracts above. Real hardware qualification remains a separate later step.
