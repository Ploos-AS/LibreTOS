# M4.4 — Aggregate Mega ST family qualification

M4.4 is the release-style qualification gate for the canonical Mega ST and Mega STe targets.

It runs, in order:

1. M4.1 canonical profile validation
2. M4.2 dedicated ROM build and Hatari boot qualification
3. M4.3 guest-side platform qualification

Run:

```sh
make qualify-m4
```

The aggregate result is written to:

- `build/m4/qualification/RESULT.json`
- `build/m4/qualification/PROFILES.json`

A PASS claim is intentionally limited to these canonical profiles:

- `mega-st-68000-4m-192k-us`
- `mega-ste-68000-4m-256k-us`

and to the M4.1-M4.3 regressions exercised by this gate.

M4.4 does not claim complete emulation or hardware coverage for every historical Mega ST or Mega STe configuration. Existing ST and STe CI jobs remain independent regression gates.
