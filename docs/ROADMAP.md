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

## M1 — Reproducible baseline + Hatari boot

Goal: produce a reproducible free ROM/runtime baseline and boot it automatically in Hatari.

Planned work:

- pin an audited EmuTOS upstream baseline
- establish the cross-toolchain
- scripted build from a clean checkout
- record hashes and build metadata
- add Hatari configuration for Atari ST / 68000
- automated boot smoke test
- archive qualification evidence

M1 does not imply that LibreTOS is already an independent implementation. Upstream-derived code and local changes must remain clearly distinguishable.

## M2 — ST compatibility profile

- formalize machine profile
- boot and API regression tests
- floppy/media tests
- GEMDOS/AES/VDI compatibility coverage
- qualification report

## Later

Potential profiles include STe, Mega ST/Mega STe, TT and Falcon. These are not M0 commitments.
