# M8.2 — Native Amiga startup/HAL contract

M8.2 defines the first low-level implementation boundary for LibreTOS running natively on classic Amiga hardware.

## Baseline

The canonical target remains `amiga-ocs-68000-1m`: Motorola 68000, OCS, 512 KiB Chip RAM plus 512 KiB Fast RAM, represented initially by A500/A2000-class systems.

LibreTOS must not depend on a proprietary Kickstart ROM for this native path.

## Startup/HAL boundary

`src/amiga/m8_startup_contract.h` establishes interfaces for:

- reset entry
- 68000 vector-table initialization
- baseline exception handling
- Chip/Fast RAM discovery
- early serial diagnostics
- deterministic halt path
- OCS custom-chip and CIA address constants

The platform layer is deliberately kept below the portable GEMDOS/AES/VDI layers.

## Qualification boundary

M8.2 is a source/profile contract gate. It verifies that the native startup interfaces exist and remain tied to the canonical OCS/68000 profile without introducing a Kickstart dependency.

It does **not** claim that LibreTOS already boots on an Amiga emulator or physical Amiga. That becomes the M8.3 runtime gate, where the reset/startup implementation must execute in an Amiga emulator and emit machine-readable evidence through the early diagnostic path.

## Exit criteria

- canonical M8.1 profile retained
- native 68000 reset/startup interface defined
- vector and exception initialization interface defined
- memory discovery interface defined
- early serial diagnostics interface defined
- no proprietary Kickstart requirement
- deterministic CI evidence from `make qualify-m8-startup`

After this gate, M8.3 implements and executes the startup path in an emulator.
