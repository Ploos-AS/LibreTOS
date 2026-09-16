# LibreTOS Roadmap

LibreTOS is developed in two deliberate phases:

1. **Atari first** — implement and qualify LibreTOS across the classic Atari 68k family.
2. **Alternative 68k targets later** — only after the Atari machine matrix is established, add non-Atari targets such as Amiga.

The Amiga target is therefore a documented future direction, not a shortcut around Atari compatibility work.

## Project-wide machine-variant policy

LibreTOS uses shared source code and common build/CI infrastructure, but **does not replace the individual Atari machine ROMs with one generic ROM**.

Every supported Atari machine profile must have a stable identifier, deterministic machine-specific build, explicit qualification path and separately named ROM/image retained as a release artifact. Adding support for a newer machine must not remove, replace or make unreproducible the ROMs for earlier supported machines.

A shared machine/profile schema exists to make the model-specific builds consistent; it is not a universal-ROM design. Machine-specific CPU, memory, video, storage, audio, BIOS/XBIOS and other hardware differences remain explicit in their profiles and qualification evidence.

Every LibreTOS release that claims support for a machine must publish that machine's qualified ROM/image separately. A universal image may be researched later as an optional convenience, but it must never replace the canonical per-machine artifacts.

The project-wide pipeline is:

**shared source → machine profile → machine-specific build → machine-specific qualification → separate retained release ROM/image**

This same preservation and release principle is used by LibreKick and LibreROM.

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

## M2 — Atari ST compatibility profile + regression suite

Goal: turn the bootable baseline into an explicitly tested Atari ST / 68000 compatibility target.

### M2.1 — Canonical machine profile

- machine-readable ST/68000 profile
- fixed CPU, RAM, ROM, display and storage assumptions
- automated profile contract check

Status: **PASS (CI)**. See `docs/M2_ST_PROFILE.md`.

### M2.2 — Boot regression

- make Hatari boot qualification consume the canonical profile
- deterministic boot evidence and failure markers

Status: **PASS (CI)**. See `docs/M2_2_BOOT_REGRESSION.md`.

### M2.3 — GEMDOS regression

- guest-side test payload
- representative file/process/system calls
- machine-readable result capture

Status: **PASS (CI)**.

### M2.4 — AES/VDI regression

- minimal AES application lifecycle coverage
- basic VDI workstation/drawing coverage

Status: **implemented; CI qualification pending**. See `docs/M2_4_AES_VDI.md`.

### M2.5 — Floppy/media regression

- redistributable floppy fixtures
- read/write cases
- media-change behavior

### M2.6 — M2 qualification

- aggregate results and evidence
- document tested compatibility boundaries

M2 does not imply complete TOS compatibility. Claims must remain tied to explicit tests and the canonical machine profile.

## M3 — Atari STe family

Goal: add a qualified STe-class target while preserving ST compatibility.

Planned scope:

- 68000 STe profile
- enhanced palette/video behavior
- DMA sound
- blitter coverage where applicable
- STe-specific BIOS/XBIOS behavior
- Hatari regression profile and qualification evidence
- retain and publish a separate STe ROM/image rather than replacing the ST artifact

Representative machines:

- Atari 520STe
- Atari 1040STe

## M4 — Mega ST and Mega STe

Goal: qualify the workstation-oriented ST variants and their platform-specific differences.

Planned scope:

- Mega ST profile
- Mega STe profile
- blitter/cache/platform-control behavior as applicable
- storage and peripheral differences
- compatibility regression against ST and STe profiles
- separate retained release artifacts for Mega ST and Mega STe profiles

Representative machines:

- Mega ST
- Mega STe

## M5 — Atari TT030

Goal: establish LibreTOS as a qualified 68030 Atari target.

Planned scope:

- Motorola 68030 profile
- TT memory model
- TT video modes
- SCSI/storage behavior
- FPU-aware qualification where applicable
- 68000 compatibility regression
- separate retained TT030 ROM/image

Representative machine:

- Atari TT030

## M6 — Atari Falcon030

Goal: support and qualify the most advanced classic Atari 68k desktop target in the initial family roadmap.

Planned scope:

- Motorola 68030 profile
- Falcon video modes
- IDE/storage support
- Falcon audio architecture
- DSP-facing OS interfaces and behavior
- compatibility regression against earlier Atari targets
- separate retained Falcon030 ROM/image

Representative machine:

- Atari Falcon030

## M7 — Atari family convergence and multi-model release

Goal: make the individual Atari profiles one coherent LibreTOS platform family while preserving them as separate machine-specific ROM/image builds.

Exit criteria:

- shared machine/profile schema that does not collapse model-specific builds
- ST, STe, Mega ST/Mega STe, TT030 and Falcon030 profiles represented in CI where automation is practical
- deterministic machine-specific build for every retained profile
- common GEMDOS/AES/VDI regression suite
- machine-specific BIOS/XBIOS regression coverage
- documented compatibility matrix
- documented hardware/emulator qualification boundaries
- release packaging that publishes each supported machine ROM/image as a separate artifact
- no regression, replacement or silent removal of earlier qualified profiles when later machine support lands

**Gate:** M7 is the planned prerequisite for beginning the Amiga platform implementation.

## M8 — Amiga native target foundation

Goal: boot LibreTOS as a native operating environment on classic Amiga 68k hardware without pretending that the Amiga is an Atari machine.

Initial direction:

- Motorola 68000 native execution
- Amiga-specific low-level boot/HAL
- chip RAM and memory discovery
- exception/vector setup
- CIA/timer/keyboard/serial bring-up
- OCS/ECS baseline first
- emulator qualification before real-hardware qualification

The Atari GEMDOS/AES/VDI layers should remain as portable as practical; Amiga-specific behavior belongs below or beside those layers.

See `docs/AMIGA_TARGET.md`.

## M9 — Amiga GEMDOS + program execution

Goal: run well-behaved Atari/TOS 68k applications directly on the Amiga CPU where they depend on operating-system interfaces rather than Atari hardware registers.

Planned scope:

- GEMDOS-compatible filesystem/process services
- `.PRG` loading and relocation
- TOS basepage/process environment
- BIOS/XBIOS translation where feasible
- explicit compatibility classification for applications

No 68000 CPU emulation is intended for ordinary portable TOS applications; their 68k instructions execute natively.

## M10 — Amiga VDI/AES/GEM

Goal: provide a usable GEM environment backed by Amiga graphics hardware.

Planned scope:

- planar OCS/ECS VDI driver
- fonts, lines, rectangles and raster operations
- Amiga Blitter acceleration for suitable VDI operations
- AES application lifecycle
- GEM Desktop qualification
- later AGA profile as a separate extension

A major demonstration milestone is **GEM Desktop running natively on Amiga hardware under LibreTOS**.

## M11 — Amiga custom-chip extensions

Goal: make Amiga hardware a first-class extension platform rather than merely an implementation detail.

Candidate LibreTOS/Amiga extension interfaces:

- Blitter
- Copper
- hardware sprites
- Paula audio
- CIA services
- chipset capability discovery
- optional AGA extensions

These interfaces must be additive. Portable Atari applications should continue to use standard GEMDOS/AES/VDI/BIOS/XBIOS interfaces, while Amiga-aware applications may opt into accelerated or Amiga-specific features.

## M12 — Atari hardware-access compatibility layer on Amiga

Goal: extend compatibility beyond well-behaved TOS applications without turning the entire Amiga target into a full Atari emulator.

Compatibility classes:

- **L0** — GEMDOS/CLI applications: native
- **L1** — GEM/AES/VDI applications: native
- **L2** — BIOS/XBIOS-dependent applications: translated/shimmed
- **L3** — limited direct Atari hardware access: traps/shims where practical
- **L4** — hardware-banging ST software, games and demos: hybrid/emulation path
- **L5** — Falcon/DSP-heavy or deeply hardware-coupled software: later research

The separate **Amtari** project is the natural place for the heavier Atari hardware emulation needed by L4/L5-class software. LibreTOS should prefer native execution and translation whenever possible.

## Long-term direction

LibreTOS should remain an Atari-compatible operating environment first. The Amiga work explores a broader idea: a portable TOS/GEM environment on another 68k platform, with native 68k application execution and optional access to capabilities that Atari hardware never had.

This ordering is intentional:

**Atari ST → STe → Mega ST/Mega STe → TT030 → Falcon030 → Atari family convergence → Amiga.**
