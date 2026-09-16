# M7.1 — Shared Atari machine-profile schema

M7.1 establishes one structural contract for LibreTOS Atari machine profiles without turning LibreTOS into a single-ROM project.

## Policy

The schema is shared; the ROMs are not.

Every retained Atari target continues to have its own stable profile, deterministic build, qualification evidence and separately published release ROM/image. A future universal image is allowed only as an additional convenience artifact and cannot replace any canonical per-machine image.

Current retained profile set:

- Atari ST — `st-68000-1m-192k-us`
- Atari STe — `ste-68000-1m-256k-us`
- Atari Mega ST — `mega-st-68000-4m-192k-us`
- Atari Mega STe — `mega-ste-68000-4m-256k-us`
- Atari TT030 — `tt030-68030-4m-16mtt-512k-us`
- Atari Falcon030 — `falcon030-68030-4m-512k-us`

## Contract

`config/machine-profile.schema.json` defines the common metadata envelope: machine identity, CPU/RAM, ROM parameters, display, storage and qualification requirements. `platform_features` and additional machine-specific fields deliberately remain extensible so the common schema does not erase hardware differences.

`tools/qualify_m7_profile_schema.py` provides a dependency-free CI qualification of the current profile matrix and additionally enforces unique profile IDs, unique canonical Hatari machine targets and the no-proprietary-ROM rule.

Run:

```sh
make qualify-m7-profile-schema
```

Expected result:

```text
M7.1 Atari machine-profile schema: PASS
profiles=6
machines=falcon,megast,megaste,st,ste,tt
policy=separate-machine-builds-and-release-artifacts
```

## M7.1 exit criteria

- shared schema exists
- all six retained Atari target profiles satisfy the common contract
- machine-specific extensions remain possible
- separate-build/release policy is machine-checkable
- CI runs the qualification on pushes and pull requests

M7.2 can build on this contract to introduce the common cross-machine GEMDOS/AES/VDI regression suite.
