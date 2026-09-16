# M7.5 — Atari family release bundle

M7.5 closes the Atari-family convergence milestone by defining the release bundle and aggregate no-regression gate for all retained Atari targets.

## Canonical release artifacts

Every qualified machine remains a first-class build, qualification, and release target. A conforming multi-model release contains a distinct canonical ROM/image for each retained target:

- Atari ST
- Atari STe
- Atari Mega ST
- Atari Mega STe
- Atari TT030
- Atari Falcon030

The canonical artifact names are owned by `config/targets.json`. They must be unique and the target must remain `qualified`.

## Universal ROM policy

A universal or multi-machine ROM may be produced later, but only as an additional convenience artifact. It is never the canonical replacement for any machine-specific ROM and must not supersede, hide, remove, or stop the build, qualification, retention, or publication of any machine-specific artifact.

The release model is therefore:

`shared source -> machine profile -> machine-specific build -> machine-specific qualification -> separate retained release ROM/image`

An optional universal ROM may be appended to that release set; it does not alter the canonical pipeline above.

## Qualification gate

`make qualify-m7-release-bundle` verifies the retained six-target registry, qualified state, unique canonical artifact names, machine profiles, and the no-proprietary-ROM requirement. It emits deterministic evidence under `build/m7/release-bundle/`.

The M7.5 gate depends on the earlier M7.1–M7.4 contract gates. Existing M2–M6 runtime qualification remains the authority for machine-specific runtime behavior; this aggregate release gate does not pretend to rerun those guest-side tests.

## Exit criteria

M7.5 passes when all six retained Atari targets are represented, qualified, mapped to separate unique canonical artifacts, and covered by the permanent retention policy. A universal ROM is explicitly optional and additive only. The resulting evidence can be used by later release automation to assemble the complete Atari-family release without collapsing machine variants.

After M7.5, the Atari-family convergence milestone is structurally complete and work can proceed to M8, the Amiga native-target foundation, while Atari variants remain protected by the regression and release gates.
