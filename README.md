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
- Atari machine-family implementation and qualification before alternative-platform ports

## Platform roadmap

LibreTOS is **Atari first**. The planned platform progression is:

**Atari ST → STe → Mega ST/Mega STe → TT030 → Falcon030 → Atari family convergence.**

Only after that Atari-family baseline is established does the roadmap open an alternative native 68k target: **classic Amiga**. The future Amiga port is intended to run suitable TOS 68k applications natively through LibreTOS APIs, back GEM/VDI with Amiga hardware, and eventually provide optional access to Blitter, Copper, sprites, Paula and other chipset capabilities.

Heavy direct Atari-hardware compatibility remains a separate problem and can cooperate with the sibling Amtari project rather than forcing all applications through full machine emulation.

## Milestones

- **M0** — repository, scope, provenance/compliance policy, build and CI skeleton
- **M1** — reproducible baseline build and first Hatari boot qualification
- **M2** — Atari ST/68000 compatibility profile and regression suite
- **M3** — Atari STe family
- **M4** — Mega ST and Mega STe
- **M5** — Atari TT030
- **M6** — Atari Falcon030
- **M7** — Atari family convergence and compatibility matrix
- **M8+** — future native Amiga target and TOS-on-Amiga compatibility work

See `docs/ROADMAP.md`, `docs/AMIGA_TARGET.md` and `docs/PROVENANCE.md`.

## Status

Atari implementation track active. Amiga target documented for future work after Atari-family convergence.

## Copyright

Copyright © Ploos AS.

Third-party code retains its original copyright and license terms.
