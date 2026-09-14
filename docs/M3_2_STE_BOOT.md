# M3.2 — Atari STe build + boot regression

Status: **implemented; CI qualification pending**.

M3.2 turns the canonical M3.1 Atari STe profile into a separately built and retained LibreTOS machine artifact.

## Artifact

The dedicated STe build produces:

`build/m3/ste/LibreTOS-STe-68000-192k-us.img`

The artifact is built from the same pinned free upstream baseline as the qualified ST target, but it is retained as a distinct machine target with its own name, hashes, metadata and qualification evidence. A later STe-specific divergence can therefore happen without replacing the ST artifact.

## Build

Run:

```sh
make build-m3-ste
```

Evidence includes `SHA256SUMS` and `BUILDINFO.txt` containing the pinned upstream commit, compiler, profile and artifact name.

## Boot qualification

Run:

```sh
make qualify-m3-boot
```

The qualification consumes `config/m3-ste-68000.json` and boots the dedicated STe artifact in Hatari using `--machine ste`, 68000 CPU level, 1 MiB ST-RAM and the profile-defined qualification settings.

A PASS requires Hatari to complete the configured VBL interval with no fatal TOS-load, bus-error or address-error marker. Evidence is written under `build/m3/ste-boot/`.

## Regression boundary

M3.2 does not replace M2. The existing ST build and full M2 qualification remain independent CI jobs. Adding the STe artifact extends the permanent target matrix rather than mutating the ST target.

M3.2 proves deterministic STe-target build retention and emulator boot only. STe-specific palette, DMA sound, blitter, hardware scrolling and BIOS/XBIOS behavior are covered by later M3 regressions.
