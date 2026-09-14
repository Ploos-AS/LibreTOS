# LibreTOS Roadmap

## M0 — Foundation

Goal: establish a legally and technically clean project baseline.

Exit criteria:

- project scope documented
- initial Atari ST / 68000 target documented
- provenance and licensing policy documented
- no proprietary Atari ROM material required by repository or CI
- build/qualification direction documented
- M1 plan defined

Status: **complete**.

## M1 — Reproducible baseline + Hatari boot

Goal: produce a reproducible free ROM/runtime baseline and boot it automatically in Hatari.

Completed:

- pinned audited EmuTOS upstream baseline
- Atari/MiNT cross-toolchain
- scripted clean build
- hashes and build metadata
- Hatari Atari ST / 68000 boot smoke test
- archived CI qualification evidence

See `docs/M1_QUALIFICATION.md`.

Status: **PASS (CI)**.

## M2 — ST compatibility profile + regression suite

Goal: turn the bootable baseline into an explicitly tested Atari ST / 68000 compatibility target.

### M2.1 — Canonical machine profile

- machine-readable ST/68000 profile
- fixed CPU, RAM, ROM, display and storage assumptions
- automated profile contract check

Status: **implemented**. See `docs/M2_ST_PROFILE.md`.

### M2.2 — Boot regression

- make Hatari boot qualification consume the canonical profile
- deterministic boot evidence and failure markers

### M2.3 — GEMDOS regression

- guest-side test payload
- representative file/process/system calls
- machine-readable result capture

### M2.4 — AES/VDI regression

- minimal AES application lifecycle coverage
- basic VDI workstation/drawing coverage

### M2.5 — Floppy/media regression

- redistributable floppy fixtures
- read/write cases
- media-change behavior

### M2.6 — M2 qualification

- aggregate results and evidence
- document tested compatibility boundaries

M2 does not imply complete TOS compatibility. Claims must remain tied to explicit tests and the canonical machine profile.

## M3+

Incremental LibreTOS-specific improvements and broader machine profiles. Potential profiles include STe, Mega ST/Mega STe, TT and Falcon.
