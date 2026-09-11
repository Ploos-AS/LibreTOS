# LibreTOS

LibreTOS is a Ploos AS project to build and qualify a free, redistributable TOS-compatible operating environment for classic Atari 68k systems.

## M0 scope

M0 establishes the project foundation before any compatibility claims are made.

Initial target:

- Atari ST
- Motorola 68000
- ROM-oriented boot/runtime model
- Hatari as the primary automated emulator target
- EmuTOS as the initial upstream/reference baseline where licensing and provenance permit

## Project principles

- Free and redistributable source and binaries
- No proprietary Atari ROM images in the repository or CI
- Explicit provenance and license tracking
- Reproducible, automated builds where practical
- Emulator qualification before hardware qualification
- Compatibility claims backed by tests and qualification reports

## Milestones

- **M0** — repository, scope, provenance/compliance policy, build and CI skeleton
- **M1** — reproducible baseline build and first Hatari boot qualification
- **M2** — Atari ST/68000 compatibility profile and regression suite
- **M3+** — incremental LibreTOS-specific improvements and broader machine profiles

See `docs/ROADMAP.md` and `docs/PROVENANCE.md`.

## Status

M0 foundation.

## Copyright

Copyright © Ploos AS.

Third-party code retains its original copyright and license terms.
