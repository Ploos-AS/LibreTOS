# M5.2 — Atari TT030 ROM and Hatari boot qualification

M5.2 adds a dedicated, retained LibreTOS ROM artifact for the Atari TT030 and qualifies it under the canonical M5.1 TT030 profile.

## Canonical artifact

- Target: `tt030-68030`
- Profile: `tt030-68030-4m-16mtt-512k-us`
- Artifact: `LibreTOS-TT030-68030-512k-us.img`
- ROM size: 512 KiB
- Source: pinned free upstream baseline

The TT030 image is a separate permanent artifact. It does not replace ST, STe, Mega ST, or Mega STe images.

## Hatari contract

The boot qualification explicitly runs Hatari with:

- machine: `tt`
- CPU: 68030 (`--cpulevel 3`)
- CPU clock: 32 MHz
- ST-RAM: 4 MiB
- TT-RAM: 16 MiB
- 32-bit addressing
- 68882 FPU
- MMU enabled
- 512 KiB LibreTOS ROM

The run must complete the configured VBL window without a non-zero Hatari exit, timeout, TOS load failure, or fatal emulator log marker.

## Run locally

```sh
make qualify-m5-boot
```

## Evidence

Build evidence is written under:

```text
build/m5/tt030/
```

Boot qualification evidence is written under:

```text
build/m5/tt030-boot/
```

The evidence includes the canonical profile, ROM SHA-256, exact Hatari contract, emulator log, and machine-readable qualification result.

## Scope

A PASS proves deterministic boot of the pinned free 512 KiB ROM under the explicit canonical TT030 Hatari configuration. Guest-side TT hardware/API qualification and real-hardware qualification are separate later milestones.
