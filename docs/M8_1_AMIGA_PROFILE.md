# M8.1 — Native Amiga foundation profile

M8.1 begins active Amiga implementation after completion of the Atari-family M7 gate.

The first canonical target is a conservative 68000/OCS machine profile representing an Amiga 500/2000-class system. LibreTOS executes natively on the 68k CPU; the target is not configured as an Atari machine and does not require a proprietary Kickstart ROM for qualification.

## Baseline

- Motorola 68000
- OCS chipset
- 512 KiB chip RAM plus 512 KiB fast RAM baseline
- Agnus, Denise, Paula and CIA platform services
- Blitter and Copper capability recorded from the start
- native floppy-oriented bootstrap direction
- canonical artifact `LibreTOS-Amiga-OCS-68000-1M.rom`

M8.1 is a profile/foundation contract only. It does not claim that the ROM already boots or that GEMDOS/GEM applications run on Amiga. Those claims require later runtime gates.

## Platform policy

Amiga support is additive to the Atari targets. Atari ROMs remain separately built, qualified and published. Amiga machines likewise receive machine-specific profiles and artifacts as support expands to ECS, AGA and higher CPUs. A future universal Amiga image may exist only as an additional convenience artifact and must not replace canonical machine-specific builds.

## Qualification

`make qualify-m8-amiga-profile` verifies the native 68000/OCS baseline, artifact identity and absence of a proprietary Kickstart dependency. CI archives deterministic evidence under `build/m8/profile/`.

Next: M8.2 — native Amiga startup/HAL skeleton, vectors, memory discovery and serial diagnostics.
