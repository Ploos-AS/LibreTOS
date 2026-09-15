# M6.5 — Atari Falcon030 aggregate qualification

M6.5 is the aggregate qualification gate for the permanent canonical Atari Falcon030 target.

## Canonical target

- Target: `falcon030-68030`
- Profile: `config/m6-falcon030-68030.json`
- ROM: `LibreTOS-Falcon030-68030-512k-us.img`
- CPU: Motorola 68030
- ROM size: 512 KiB
- Emulator: Hatari Falcon mode

## Required regressions

`make qualify-m6` executes the complete M6 chain:

1. M6.1 canonical Falcon030 profile validation
2. M6.2 Falcon030 ROM build and boot qualification
3. M6.3 Falcon030 guest platform qualification
4. M6.4 Falcon030 enhanced interface qualification
5. permanent target-registry validation

A failure in any stage fails M6.5.

## Compatibility claim

A PASS qualifies LibreTOS for the explicit canonical Falcon030 profile and the interfaces covered by M6.1 through M6.4. It does not claim complete Falcon hardware emulation or validation.

The following remain outside the required M6.5 runtime claim:

- complete DSP56001 execution semantics
- IDE read/write semantics
- NVRAM persistence
- external audio fidelity

## Evidence

The aggregate gate writes evidence below `build/m6/qualification/`, including `RESULT.json` and the canonical `PROFILE.json`. The GitHub Actions `M6 Qualification` workflow also preserves the ROM, hashes, build metadata, and M6.2-M6.4 runtime evidence.

The Falcon030 registry status must not be changed to `qualified` until this aggregate workflow has passed on GitHub Actions.
