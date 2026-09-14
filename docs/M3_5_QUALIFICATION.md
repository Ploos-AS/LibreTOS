# M3.5 — Aggregate Atari STe qualification

M3.5 is the release-style qualification gate for the canonical Atari STe/68000 LibreTOS target.

## Canonical target

- Profile: `ste-68000-1m-256k-us`
- Machine: Atari STe
- CPU: 68000
- ST-RAM: 1 MiB
- ROM: 256 KiB US image
- Emulator: Hatari canonical `ste` profile

## Required stages

The aggregate gate runs these milestones sequentially and stops on the first failure:

1. **M3.1 profile** — validate the canonical STe profile and retained ST regression contract.
2. **M3.2 boot** — build the dedicated 256 KiB STe ROM and boot it under Hatari.
3. **M3.3 platform** — guest-side STe platform/XBIOS probe, including machine and sound cookies, screen state and blitter presence.
4. **M3.4 enhanced hardware** — deterministic reversible checks of STe enhanced hardware controls.

## Command

```sh
make qualify-m3
```

## Evidence

The aggregate runner writes:

- `build/m3/qualification/RESULT.json`
- `build/m3/qualification/PROFILE.json`

The CI job also retains the dedicated ROM and evidence directories from M3.2, M3.3 and M3.4.

A PASS means only that the explicit canonical STe profile and the regressions above are qualified. It is not a blanket compatibility claim for all STe configurations or software.
