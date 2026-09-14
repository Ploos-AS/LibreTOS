# M2.2 — Profile-driven boot regression

Status: **implemented; CI qualification pending**

M2.2 turns the canonical M2 Atari ST / 68000 profile into the single source of truth for automated Hatari boot qualification.

## Command

```sh
make qualify-m2-boot
```

The target first validates `config/m2-st-68000.json`, builds the pinned M1 ROM baseline, then runs `tools/qualify_m2_boot.py`.

## Regression contract

The runner reads these values from the profile rather than hard-coding them in a shell command:

- Hatari machine
- CPU level
- ST-RAM size
- compatible mode
- fast-boot mode
- sound mode
- minimum VBL count

The run fails when Hatari exits non-zero or its log contains known fatal ROM/emulation markers.

## Deterministic evidence

Each run writes `build/m2/boot/`:

- `PROFILE.json` — normalized canonical profile used for the run
- `ROM.sha256` — exact ROM digest
- `HATARI_PROFILE.txt` — effective profile-derived Hatari settings
- `hatari.log` — emulator log
- `RESULT.txt` — PASS/FAIL verdict and key identifiers

GitHub Actions uploads that directory as the `libretos-m2-boot-evidence` artifact.

## Scope

M2.2 provides repeatable boot-regression coverage for the canonical Atari ST / 68000 profile. It does not yet prove GEMDOS, AES/VDI, or floppy/media semantics; those are subsequent M2 stages.
