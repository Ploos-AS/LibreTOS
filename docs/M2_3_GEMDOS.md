# M2.3 — GEMDOS regression

Status: **implemented; CI qualification pending**

M2.3 adds a guest-side Atari program that executes representative GEMDOS operations inside LibreTOS under Hatari and writes a machine-readable verdict back to the host through Hatari GEMDOS drive emulation.

## Command

```sh
make qualify-m2-gemdos
```

## Guest coverage

`tests/m2/gemdos_probe.c` is built for Motorola 68000 with the Atari/MiNT cross-toolchain and autostarted as `C:\\GEMDOS.TOS`.

The probe exercises:

- `Dgetdrv`
- `Dcreate`
- `Ddelete`
- `Fcreate`
- `Fwrite`
- `Fclose`
- `Fopen`
- `Fread`
- payload comparison
- `Fdelete`
- `Pterm`

A successful guest run writes `C:\\M2GEMDOS.TXT` with `status=PASS`. Missing output, a failed stage, Hatari failure, or known fatal emulator markers fail qualification.

## Evidence

CI archives `build/m2/gemdos/`, including normalized profile metadata, ROM and probe hashes, effective Hatari settings, guest verdict and Hatari log.

## Scope

This stage establishes representative GEMDOS filesystem/process regression coverage on the canonical Atari ST / 68000 profile. It is not a claim of complete GEMDOS compatibility; coverage grows incrementally with later regression cases.
