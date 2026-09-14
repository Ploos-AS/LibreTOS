# M2.6 — Atari ST qualification

Status: **implemented; CI qualification pending**.

M2.6 is the aggregate qualification gate for LibreTOS M2. It does not broaden compatibility claims beyond the tests already defined by M2.1–M2.5.

## Canonical target

The qualified target is the machine-readable `st-68000-1m-192k-us` profile in `config/m2-st-68000.json`: Atari ST class, Motorola 68000, 1 MiB ST-RAM and the pinned free 192 KiB US ROM baseline.

## Aggregate gate

Run:

```sh
make qualify-m2
```

The gate executes, in order:

- M2.1 canonical profile contract
- M2.2 deterministic Hatari boot regression
- M2.3 guest-side GEMDOS regression
- M2.4 guest-side AES/VDI regression
- M2.5 floppy/media regression

Any failed stage fails M2.6. A successful run writes `build/m2/qualification/RESULT.json` and a copy of the exact canonical profile used for the qualification.

## Compatibility boundary

A PASS means that the pinned LibreTOS baseline satisfies the explicit automated regressions above on the canonical Hatari ST/68000 profile. It does **not** claim complete TOS compatibility, compatibility with all Atari ST software, cycle-exact hardware behavior, copy-protected floppy compatibility, hot media-change timing, or qualification on physical Atari hardware.

Those boundaries remain explicit so later STe, Mega, TT and Falcon work can extend the matrix without weakening the meaning of an existing PASS.

## Evidence

The CI `m2-qualification` job archives the aggregate result plus the detailed boot, GEMDOS, AES/VDI and media evidence directories. This makes M2.6 a single machine-readable gate while retaining the evidence from each constituent regression.
