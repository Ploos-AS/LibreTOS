# M2.4 — AES/VDI regression

Status: **implemented; CI qualification pending**

M2.4 adds guest-side regression coverage for the GEM AES and VDI ABI on the canonical Atari ST / 68000 profile.

## Command

```sh
make qualify-m2-aes-vdi
```

The qualification target builds the pinned LibreTOS ROM, compiles `tests/m2/aes_vdi_probe.c` for Motorola 68000, mounts a writable GEMDOS hard-disk directory in Hatari and autostarts the probe as a GEM program.

## AES coverage

The probe invokes AES through trap #2 directly, without depending on a host-side GEM helper library:

- `appl_init`
- `graf_handle`
- `appl_exit`

The returned AES application ID and physical workstation handle are validated and recorded.

## VDI coverage

The probe invokes VDI through trap #2 directly:

- `v_opnvwk`
- `v_pline`
- `v_clsvwk`

A virtual workstation must open successfully. A basic line primitive is submitted before the workstation is closed.

## Evidence

The guest writes `C:\\M2AESVD.TXT` into the mounted host directory. CI normalizes that into `build/m2/aes-vdi/RESULT.txt` and archives:

- canonical profile
- ROM SHA-256
- probe SHA-256
- effective Hatari profile
- guest result
- Hatari log

M2.4 proves representative AES application lifecycle and basic VDI workstation/drawing calls on the canonical profile. It is not a claim of complete GEM compatibility.
