# LibreTOS multi-target policy

LibreTOS is one source tree with permanent, separately named Atari machine targets.

Adding a new machine never replaces an older qualified build. Every target keeps its own machine profile, ROM/build configuration, artifact name, hashes and qualification evidence. Later milestones must continue to build and regress earlier qualified targets.

The canonical target registry is `config/targets.json` and is checked by `tools/check_targets.py`.

## Initial Atari matrix

| Target | CPU | Milestone | Artifact | Status |
| --- | --- | --- | --- | --- |
| Atari ST | 68000 | M2 | `LibreTOS-ST-68000-192k-us.img` | qualified |
| Atari STe | 68000 | M3 | `LibreTOS-STe-68000-192k-us.img` | planned |
| Atari Mega ST | 68000 | M4 | `LibreTOS-MegaST-68000-192k-us.img` | planned |
| Atari Mega STe | 68000 | M4 | `LibreTOS-MegaSTe-68000-192k-us.img` | planned |
| Atari TT030 | 68030 | M5 | `LibreTOS-TT030-68030-512k-us.img` | planned |
| Atari Falcon030 | 68030 | M6 | `LibreTOS-Falcon030-68030-512k-us.img` | planned |

ROM sizes for future, not-yet-qualified machines are part of the current target contract and may be corrected before those targets become qualified if upstream/platform requirements demand it. Once a target is qualified, incompatible changes require an explicit profile/version transition rather than silent replacement.

## Qualification rule

A target may move through `planned` → `implemented` → `qualified`. A `qualified` target must have an existing canonical machine profile and remain present in CI regression coverage. M3 and later milestones therefore extend a matrix instead of advancing a single mutable machine definition.
