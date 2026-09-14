# M4.2 — Mega ST / Mega STe ROM build and boot qualification

M4.2 turns the canonical M4.1 machine profiles into retained, model-specific LibreTOS ROM artifacts and verifies that both boot in Hatari.

## Artifacts

- Mega ST: `build/m4/mega/LibreTOS-MegaST-68000-192k-us.img`
- Mega STe: `build/m4/mega/LibreTOS-MegaSTe-68000-256k-us.img`

Both are built from the pinned free EmuTOS baseline recorded in `config/upstream.env`. The artifacts are retained separately and do not replace the qualified ST or STe ROMs.

## Canonical boot profiles

### Mega ST

- profile: `mega-st-68000-4m-192k-us`
- Hatari machine: `megast`
- CPU: 68000
- RAM: 4 MiB
- ROM: 192 KiB, US

### Mega STe

- profile: `mega-ste-68000-4m-256k-us`
- Hatari machine: `megaste`
- CPU: 68000
- RAM: 4 MiB
- ROM: 256 KiB, US

The boot qualifier runs each target independently for the profile-defined minimum VBL count, checks Hatari's return code and rejects explicit ERROR/FATAL or TOS-loading failures.

## Commands

```sh
make build-m4-mega
make qualify-m4-boot
```

`make qualify-m4-boot` first re-validates M4.1 profiles, rebuilds both pinned ROM artifacts, and then runs the two Hatari boot regressions.

## Evidence

The qualifier stores evidence below `build/m4/mega-boot/`, including copied profiles, ROM hashes, effective Hatari settings, per-machine logs and results, and aggregate `RESULT.json` / `RESULT.txt` files.

GitHub Actions uploads the ROMs and evidence as `libretos-m4-mega-boot-evidence`.

A PASS claim for M4.2 means only that the two canonical Mega-family ROM artifacts were reproducibly built from the pinned free baseline and completed their bounded Hatari boot regressions. Hardware-specific Mega functionality is qualified in later M4 stages.
