# M2 Atari ST / 68000 Compatibility Profile

Status: **M2.1 implemented; qualification contract active**

M2 starts by freezing one canonical machine profile. Compatibility tests must target this profile unless a test explicitly declares another profile.

## Canonical profile

Machine-readable definition: `config/m2-st-68000.json`

- Atari ST
- Motorola 68000, Hatari CPU level 0
- 8 MHz CPU
- 1 MiB ST-RAM
- no Fast RAM
- 192 KiB US ROM baseline
- color monitor, ST-low initial display
- one floppy drive
- ROM boot; hard disk not required
- Hatari compatible mode enabled
- fast boot disabled
- at least 500 VBLs for boot qualification
- no proprietary Atari ROM required

## Contract

Run:

```sh
make qualify-m2-profile
```

The checker validates the machine-readable profile and fails if the baseline drifts from the M2 contract.

## Next M2 slices

1. **M2.2 Boot regression** — make the M1 boot smoke test consume the profile and record deterministic evidence.
2. **M2.3 GEMDOS regression** — add a small guest-side program exercising representative GEMDOS calls and result capture.
3. **M2.4 AES/VDI regression** — add minimal application/display API coverage.
4. **M2.5 Floppy/media regression** — boot/read/write/media-change cases using redistributable images.
5. **M2.6 Qualification report** — aggregate evidence and close M2.

M2 compatibility claims remain limited to tested behavior on the canonical profile.
