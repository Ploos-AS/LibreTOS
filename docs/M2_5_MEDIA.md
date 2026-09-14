# M2.5 — Floppy/media regression

Status: **implemented; CI qualification pending**.

M2.5 adds deterministic floppy-media coverage to the canonical Atari ST / 68000 profile.

## Qualification command

```sh
make qualify-m2-media
```

The qualification harness creates two redistributable 720 KiB FAT12 `.ST` images from scratch. No proprietary Atari disk material is used.

Each image contains a distinct `A:\\FIXTURE.TXT` marker (`MEDIA-A` or `MEDIA-B`). The same guest probe is then run twice in Hatari, once with each disk mounted as drive A:.

The guest verifies:

- fixture file can be opened and read from A:
- the mounted media marker is identified correctly
- `A:\\PERSIST.TXT` is absent before the write, proving a clean medium
- a new floppy file can be created and written
- the file can be reopened and read back byte-for-byte
- the write persists into the host-side `.ST` image

The host harness additionally verifies that both floppy-image hashes change after the guest writes to them. Because MEDIA-B starts clean after MEDIA-A has been modified, the two-pass sequence also catches accidental state leakage when media is replaced between emulator sessions.

Hatari is run with `--disk-a` and `--protect-floppy off` so writes target the floppy image rather than a virtual hard-disk fixture.

## Evidence

CI archives:

- canonical profile
- ROM SHA-256
- guest probe SHA-256
- effective Hatari profile
- normalized JSON result
- final disk-image SHA-256 values
- Hatari logs for MEDIA-A and MEDIA-B

## Scope boundary

M2.5 covers filesystem-visible floppy read/write behavior and deterministic media replacement across clean Hatari sessions. It does not yet claim hot eject/insert timing or FDC-level copy-protection compatibility; those remain candidates for later hardware/FDC-specific regression work.
