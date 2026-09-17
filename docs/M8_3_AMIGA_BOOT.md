# M8.3 — Native Amiga boot/runtime gate

M8.3 turns the M8.1 machine profile and M8.2 startup/HAL interface into an emulator-facing native boot contract.

The canonical baseline remains `amiga-ocs-68000-1m`: Motorola 68000, OCS, native 68k execution. LibreTOS must not require or redistribute proprietary Kickstart, Workbench, or other AmigaOS files for this gate.

## Required runtime evidence

A conforming emulator backend must prove, from a cold reset, that LibreTOS reaches the native reset entry, installs the baseline vector table, completes initial memory discovery, activates serial diagnostics, and reaches either the controlled halt path or the next runtime handoff.

`make qualify-m8-boot` currently validates and emits the deterministic M8.3 boot manifest and repository-side evidence. Its result deliberately records the emulator runtime gate as `PENDING`; this static contract is not itself a claim that LibreTOS has already booted in an Amiga emulator.

The next M8.3 implementation step is therefore to connect this manifest to a redistributable CI-capable Amiga emulator/runtime path and replace `PENDING` with captured guest/runtime evidence only after those markers are observed.

## Artifact policy

The Amiga OCS/68000 image remains a machine-specific LibreTOS artifact. Any future universal Amiga image is additive only and must never replace, hide, or stop qualification/publication of canonical per-machine images.
