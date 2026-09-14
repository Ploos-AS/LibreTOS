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
- the file can be closed, reopened and read back byte-for-byte
- the second independently generated medium is also clean and exposes its own marker

The qualification verdict is based on those guest-observed floppy filesystem semantics. Host-side `.ST` hashes before and after each run are retained as diagnostic evidence only.

This distinction is intentional: Hatari 2.4.1 can satisfy guest write/readback semantics while a run terminated by `--run-vbls` does not necessarily flush the modified raw floppy image back to the host file before exit. Requiring the host image SHA-256 to change therefore produced a false negative and is not a valid compatibility criterion for this test harness.

Hatari is run with `--disk-a` and `--protect-floppy off` so the guest exercises floppy I/O rather than the GEMDOS hard-disk fixture.

## Evidence

CI archives:

- canonical profile
- ROM SHA-256
- guest probe SHA-256
- effective Hatari profile
- normalized JSON result
- initial/final disk-image SHA-256 values as informational diagnostics
- Hatari logs for MEDIA-A and MEDIA-B

## Scope boundary

M2.5 covers filesystem-visible floppy read/write behavior and deterministic media replacement across clean Hatari sessions. It does not claim host-image flush behavior, hot eject/insert timing, or FDC-level copy-protection compatibility; those remain candidates for later emulator/hardware-specific regression work.
