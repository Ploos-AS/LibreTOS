# M7.2 — Cross-machine GEMDOS/AES/VDI regression contract

M7.2 gives every retained Atari machine target the same common operating-system regression contract while preserving separate machine ROMs.

The common contract covers three portable OS surfaces:

- GEMDOS
- AES
- VDI

The retained matrix is Atari ST, STe, Mega ST, Mega STe, TT030 and Falcon030. Each row references its own machine profile and its own unique release artifact. The shared regression contract therefore does not create, require or imply a universal ROM.

`tools/qualify_m7_common_regressions.py` validates the matrix and writes deterministic evidence under `build/m7/common-regressions/`.

Run:

```sh
make qualify-m7-common
```

Expected contract result:

```text
M7.2 common Atari regression matrix: PASS
targets=6 suites=gemdos,aes,vdi
```

## Runtime layering

M2 already provides guest-side GEMDOS and AES/VDI probes. M7.2 promotes those interfaces to a family-wide contract. Machine-specific runtime harnesses remain responsible for booting and probing their dedicated ROM/image; later M7 work can consolidate the repeated Hatari execution mechanics without weakening the per-machine qualification gates.

This separation is intentional: common GEMDOS/AES/VDI semantics are shared, while BIOS/XBIOS and enhanced-hardware behavior remains machine-specific and is handled by M7.3.

## Exit criteria

- all six retained Atari targets participate in the common regression matrix
- GEMDOS, AES and VDI are mandatory common suites
- every target references a distinct release artifact
- proprietary Atari ROMs are not required
- CI produces deterministic M7.2 matrix evidence
- machine-specific BIOS/XBIOS coverage remains separate
