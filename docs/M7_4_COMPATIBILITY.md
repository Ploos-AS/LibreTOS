# M7.4 — Compatibility matrix and qualification boundaries

M7.4 makes the Atari-family compatibility claim explicit without collapsing distinct machines into a lowest-common-denominator target.

## Compatibility model

Every retained target must satisfy the common LibreTOS contract: GEMDOS, AES, VDI, BIOS baseline, and the common XBIOS video boundary. Machine-specific capabilities are then qualified in addition to that baseline.

The retained targets are ST, STe, Mega ST, Mega STe, TT030, and Falcon030. STe, TT030, and Falcon030 keep their enhanced-hardware qualification boundaries; Mega ST and Mega STe keep their own platform boundaries. A feature qualified for one machine is not automatically claimed for another.

## Artifact boundary

Every target remains tied to its own stable machine profile and canonical ROM artifact. The compatibility matrix must contain six distinct artifacts. A universal or multi-machine ROM may later be published as an additional convenience artifact only. It must never replace, supersede, hide, or remove any canonical machine-specific ROM.

## Evidence

`tools/qualify_m7_compatibility.py` validates that all retained targets are qualified, have distinct canonical artifacts, have proprietary-ROM-independent qualification profiles, and expose explicit common and machine-specific compatibility boundaries. Evidence is written to `build/m7/compatibility/`.

M7.4 is an aggregate contract gate. Runtime authority remains with the machine-specific M2–M6 qualification harnesses and their guest-side probes.

## Exit criteria

M7.4 is complete when all six retained targets are represented, all are marked qualified, common compatibility claims are explicit, machine-specific claims remain scoped to their target, artifacts remain distinct, and the M7.4 CI gate passes.

Next: M7.5 — multi-model release bundle and aggregate Atari-family no-regression gate.
