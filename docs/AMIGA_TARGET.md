# LibreTOS Amiga Target

## Status

**Future platform target — implementation intentionally deferred until the Atari family roadmap has converged through M7.**

LibreTOS is an Atari-compatible operating environment first. The Amiga target must not displace or dilute the work required to implement and qualify the classic Atari 68k machine family.

## Why an Amiga target is interesting

Classic Atari ST-family computers and classic Amigas share Motorola 68k CPUs. This creates an unusual opportunity: many TOS applications that use documented operating-system interfaces can potentially execute their 68k application code directly on an Amiga CPU rather than through CPU emulation.

The operating environment would provide TOS-compatible services while an Amiga-specific hardware abstraction layer drives the actual Amiga hardware.

Conceptually:

```text
Atari/TOS .PRG
      |
 native 68k execution
      |
 LibreTOS
 GEMDOS / BIOS / XBIOS
 AES / VDI / GEM
      |
 Amiga platform layer
      |
 Agnus / Denise / Paula / CIA
 Blitter / Copper / sprites / audio
```

This is not intended to claim that Atari and Amiga hardware are interchangeable. Direct accesses to Atari hardware registers require separate compatibility mechanisms.

## Development ordering

The planned ordering is:

1. Atari ST
2. Atari STe
3. Mega ST / Mega STe
4. Atari TT030
5. Atari Falcon030
6. Atari-family convergence and regression matrix
7. Amiga native target

The Atari-family convergence milestone is the gate before active Amiga implementation begins.

## Design principles

### Native 68k first

Well-behaved TOS applications should execute directly on the host 68k CPU whenever possible. LibreTOS should not emulate a 68000 merely to run ordinary 68000 application instructions on a compatible 68000-family processor.

### Translate operating-system interfaces

Applications using GEMDOS, AES, VDI, BIOS and XBIOS should be served by LibreTOS implementations backed by the Amiga platform layer.

### Isolate machine-specific code

Amiga hardware support should live below or beside portable LibreTOS subsystems. Atari-specific assumptions must not leak unnecessarily into GEMDOS, AES or VDI, and Amiga-specific assumptions must not damage Atari targets.

### Exploit Amiga hardware deliberately

The Amiga target should not merely imitate an ST framebuffer. Appropriate operations may use:

- Blitter acceleration
- Copper
- hardware sprites
- Paula audio
- CIA timers and I/O
- OCS/ECS capabilities
- later AGA capabilities

### Preserve portable TOS compatibility

Amiga extensions are additive. An ordinary TOS application should not need to know it is running on an Amiga.

## Proposed implementation milestones

### Amiga foundation

- native 68000 startup
- memory/chip-RAM discovery
- vectors and exceptions
- timer
- keyboard
- serial diagnostics
- OCS/ECS baseline

### GEMDOS and `.PRG` execution

- TOS `.PRG` loader and relocation
- basepage/process environment
- filesystem services
- console applications
- standard GEMDOS regression payloads shared with Atari targets

### VDI/AES/GEM

- planar Amiga graphics backend
- fonts and primitives
- raster operations
- Blitter acceleration where appropriate
- AES lifecycle
- GEM Desktop

A key demonstration target is a usable GEM Desktop booting natively on an Amiga.

## Amiga extension API

A later optional extension API may expose capabilities unavailable through standard Atari interfaces. Candidate capability groups include:

```text
LIBRETOS_AMIGA_BLITTER
LIBRETOS_AMIGA_COPPER
LIBRETOS_AMIGA_SPRITES
LIBRETOS_AMIGA_PAULA
LIBRETOS_AMIGA_CIA
LIBRETOS_AMIGA_AGA
```

The exact ABI/API is intentionally unspecified until the base Amiga port exists. Capability discovery is preferable to applications assuming a particular chipset.

Possible future interfaces may expose accelerated services rather than raw hardware registers, allowing LibreTOS to retain control over resources.

## Compatibility classes

### L0 — GEMDOS / command-line applications

Expected path: native 68k execution with LibreTOS GEMDOS services.

### L1 — GEM/AES/VDI applications

Expected path: native 68k execution with LibreTOS GEM and the Amiga VDI backend.

### L2 — BIOS/XBIOS applications

Expected path: native execution with translated or shimmed machine services where semantics can reasonably be reproduced.

### L3 — limited direct Atari hardware access

Possible path: compatibility traps, shims or narrowly scoped translation. Feasibility depends on the software and access pattern.

### L4 — hardware-banging ST software

Games, demos and other programs that depend heavily on Atari memory maps, timing and custom hardware generally require a hybrid or emulated Atari hardware environment.

### L5 — deeply Falcon/DSP-specific software

Deferred research area. Such software may require substantial Falcon hardware emulation.

## Relationship with Amtari

LibreTOS and Amtari should solve different layers of the problem.

**LibreTOS** owns the TOS-compatible operating environment, native application path, GEMDOS/AES/VDI implementation and Amiga platform backend.

**Amtari** is the natural companion for increasingly complete Atari hardware compatibility when applications bypass operating-system interfaces.

A future dispatcher/runtime may therefore choose between:

```text
TOS application
   |
   +-- portable / OS-driven ------> native LibreTOS execution
   |
   +-- limited HW dependency -----> LibreTOS compatibility shim
   |
   +-- heavy Atari HW dependency -> Amtari-assisted execution
```

This avoids imposing full machine emulation on software that does not require it.

## Qualification strategy

The Amiga target should follow the same evidence-oriented philosophy as the Atari targets:

- reproducible build
- canonical machine profiles
- emulator qualification
- machine-readable guest results
- regression tests shared with Atari targets where meaningful
- explicit compatibility claims
- real-hardware qualification after emulator qualification

Initial emulator targets can be selected when implementation begins. Real hardware profiles should start conservatively with a baseline 68000 OCS/ECS machine before accelerators and AGA are added.

## Non-goals for the first Amiga implementation

The first Amiga target does not need to:

- emulate every Atari hardware register
- run every ST game or demo
- emulate Falcon DSP hardware
- expose raw Amiga custom-chip programming as the primary application API
- replace Amtari

The first objective is much cleaner: **boot LibreTOS on Amiga, run native 68k TOS applications through standard OS interfaces, and make GEM use Amiga hardware effectively.**
